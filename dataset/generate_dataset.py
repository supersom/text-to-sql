"""
Phase 1: Golden Dataset Generation
Run once: python dataset/generate_dataset.py
Expands 12 seed queries into 50-100 variations using Claude.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import anthropic
from config import (
    ANTHROPIC_API_KEY,
    MODEL,
    SEED_QUERIES_PATH,
    GOLDEN_DATASET_PATH,
    VARIATIONS_PER_SEED,
)
from db.database import get_schema_str

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

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


def generate_variations(seed: dict, n: int = VARIATIONS_PER_SEED) -> list[dict]:
    prompt = f"""Generate {n} variations of this question for our eval dataset.

Original question: {seed['question']}
Ground-truth SQL: {seed['ground_truth_sql']}
Complexity: {seed['complexity']}
Operations: {seed['operations']}
Risk level: {seed['risk_level']}

Return a JSON array of {n} objects with keys: question, ground_truth_sql, notes."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip().rstrip("```").strip()

    return json.loads(text)


def build_golden_dataset() -> None:
    seeds = json.loads(SEED_QUERIES_PATH.read_text())
    golden = list(seeds)  # seeds are included as-is

    print(f"Expanding {len(seeds)} seed queries with {VARIATIONS_PER_SEED} variations each...")

    for i, seed in enumerate(seeds, 1):
        print(f"  [{i}/{len(seeds)}] {seed['id']}: {seed['question'][:60]}...")
        try:
            variations = generate_variations(seed)
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

    GOLDEN_DATASET_PATH.write_text(json.dumps(golden, indent=2))
    print(f"\nDone. Golden dataset: {len(golden)} entries → {GOLDEN_DATASET_PATH}")


if __name__ == "__main__":
    build_golden_dataset()
