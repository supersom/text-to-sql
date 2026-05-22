"""
Phase 1: Golden Dataset Generation
Run once: python dataset/generate_dataset.py
Expands 12 seed queries into 50-100 variations using Claude.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    MODEL,
    SEED_QUERIES_PATH,
    GOLDEN_DATASET_PATH,
    VARIATIONS_PER_SEED,
)
from db.database import get_schema_str
from agents.llm import chat

SCHEMA = get_schema_str()

SYSTEM_PROMPT = f"""You are a data generation assistant for an insurance analytics platform.
You will generate natural language question variations for a Text-to-SQL evaluation dataset.

Database schema for context:
{SCHEMA}

Rules for generating variations:
1. Paraphrase the question using different vocabulary (formal, informal, business-speak)
2. Add temporal modifiers: "last quarter", "in Q1 2024", "since January", "year to date", "in the past 6 months"
3. Change entity names or values while keeping the intent: different risk levels, statuses, departments
4. Introduce minor typos or ambiguity (1-2 per batch) to test robustness
5. Keep the SQL semantically equivalent to the original ground-truth SQL — or note if a variation requires a different SQL

Respond with a JSON array only. Each item must have:
- "question": the variation text
- "ground_truth_sql": valid SQLite SQL that answers this question (can differ from seed if needed)
- "notes": brief explanation of what changed (e.g., "paraphrase", "temporal modifier", "typo: 'ammount'")
"""


def generate_variations(seed: dict, n: int = VARIATIONS_PER_SEED, api_key: str | None = None, backend: str | None = None, model: str | None = None) -> list[dict]:
    prompt = f"""Generate {n} variations of this question for our eval dataset.

Original question: {seed['question']}
Ground-truth SQL: {seed['ground_truth_sql']}
Complexity: {seed['complexity']}
Operations: {seed['operations']}
Risk level: {seed['risk_level']}

Return a JSON array of {n} objects with keys: question, ground_truth_sql, notes."""

    text = chat(model or MODEL, SYSTEM_PROMPT, prompt, max_tokens=2000, cache_system=True, api_key=api_key, backend=backend)
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip().rstrip("```").strip()

    return json.loads(text)


def build_golden_dataset(api_key: str | None = None, backend: str | None = None, model: str | None = None, seed_path: Path | None = None, output_path: Path | None = None) -> None:
    seed_path = seed_path or SEED_QUERIES_PATH
    output_path = output_path or GOLDEN_DATASET_PATH

    seeds = json.loads(seed_path.read_text())
    golden = list(seeds)  # seeds are included as-is

    print(f"Expanding {len(seeds)} seed queries with {VARIATIONS_PER_SEED} variations each...")

    for i, seed in enumerate(seeds, 1):
        print(f"  [{i}/{len(seeds)}] {seed['id']}: {seed['question'][:60]}...")
        try:
            variations = generate_variations(seed, api_key=api_key, backend=backend, model=model)
            for j, var in enumerate(variations):
                entry = {
                    "id": f"{seed['id']}_v{j+1}",
                    "question": var["question"],
                    "ground_truth_sql": var["ground_truth_sql"],
                    "complexity": seed["complexity"],
                    "operations": seed["operations"],
                    "risk_level": seed["risk_level"],
                    "domain": seed["domain"],
                    "source": f"generated_from_{seed['id']}",
                    "notes": var.get("notes", ""),
                }
                golden.append(entry)
        except Exception as e:
            print(f"    Warning: failed to generate variations for {seed['id']}: {e}")

    output_path.write_text(json.dumps(golden, indent=2))
    print(f"\nDone. Golden dataset: {len(golden)} entries → {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=Path, default=None, help="Path to seed queries JSON")
    parser.add_argument("--output", type=Path, default=None, help="Path to write golden dataset JSON")
    parser.add_argument("--backend", default=None, help="LLM backend (api, claude-cli, gemini-cli, codex-cli)")
    parser.add_argument("--model", default=None, help="Model string override")
    args = parser.parse_args()
    build_golden_dataset(backend=args.backend, model=args.model, seed_path=args.seed, output_path=args.output)
