#!/usr/bin/env python3
"""
DSPy-based prompt optimization for all inference-time LLM-backed agents.

Covers:
  1. agents/planner.py       — _INSTRUCTIONS   (PlanSignature)
  2. agents/sql_generator.py — _INSTRUCTIONS   (SQLGenSignature)
  3. evaluation/metrics.py   — ACCURACY_JUDGE_SYSTEM  (AccuracyJudgeSignature)
                             — RELEVANCE_SYSTEM        (RelevanceJudgeSignature)

Not covered:
  dataset/generate_dataset.py — SYSTEM_PROMPT is a one-shot data-generation prompt;
  there is no ground-truth metric to optimize it against.

Strategy:
  Planner + SQL generator are optimized *jointly* as a TextToSQLPipeline using
  MIPROv2 with execution_accuracy as the end-to-end metric. Joint optimization
  avoids the "stub planner metric" problem in the original implementation.

  Judge prompts are wrapped as DSPy modules and optimized with BootstrapFewShot
  using held-out labelled judge examples. They are lower priority; skip with
  --skip-judges if budget is tight.

Usage:
  python optimize_prompts.py [--max-train N] [--output-dir DIR] [--api-key KEY]
                             [--skip-judges] [--optimizer {mipro,bootstrap}]
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import dspy
from dspy.teleprompt import BootstrapFewShot, MIPROv2

from config import MODEL, GOLDEN_DATASET_PATH, USE_SCHEMA_RETRIEVAL
from dataset.generate_dataset import build_golden_dataset
from db.database import init_db, get_schema_str
from db.schema_store import build_schema_store, retrieve_schema
from evaluation.metrics import execution_accuracy


# ── LM configuration ──────────────────────────────────────────────────────────

def configure_lm(model: str, api_key: str | None = None) -> None:
    """Configure DSPy's global LM via LiteLLM.

    `model` must be a full LiteLLM model string, e.g.:
      anthropic/claude-sonnet-4-6
      openai/gpt-4o
      openrouter/google/gemini-2.5-pro
    """
    lm = dspy.LM(model, api_key=api_key)
    dspy.configure(lm=lm)


# ── Signatures ────────────────────────────────────────────────────────────────
# Signatures serve as the optimizable prompt surface.  The docstring becomes
# the system instruction; DSPy replaces it with a better one after optimization.

class PlanSignature(dspy.Signature):
    """Generate a structured query plan from a natural language question and schema.

    Your plan must include:
    TABLES: which tables are needed
    JOINS: which tables to join and on what keys
    FILTERS: WHERE conditions (values, date ranges, status filters)
    AGGREGATIONS: COUNT, SUM, AVG, GROUP BY, ORDER BY, LIMIT
    INTENT: one sentence describing what the user wants

    Be concise. Output plain text, not JSON or markdown.
    Only SELECT-oriented plans are valid."""

    question: str = dspy.InputField(desc="Natural language question about insurance data")
    db_schema: str = dspy.InputField(desc="Relevant database schema")
    plan: str = dspy.OutputField(
        desc="Structured query plan covering TABLES, JOINS, FILTERS, AGGREGATIONS, INTENT"
    )


class SQLGenSignature(dspy.Signature):
    """Generate a valid SQLite SELECT statement from a question, query plan, and schema.

    STRICT RULES:
    - Only SELECT statements. Never use DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE.
    - Use SQLite-compatible syntax: strftime(), julianday(), date() for date operations.
    - Always use table aliases for readability.
    - Return ONLY the raw SQL query — no markdown, no explanation, no code fences.
    - If the question cannot be answered with the available schema, return:
        SELECT 'Query out of scope' as message"""

    question: str = dspy.InputField(desc="Original natural language question")
    plan: str = dspy.InputField(desc="Structured query plan from the planner")
    db_schema: str = dspy.InputField(desc="Relevant database schema")
    sql: str = dspy.OutputField(desc="Valid SQLite SELECT statement answering the question")


class AccuracyJudgeSignature(dspy.Signature):
    """Judge semantic equivalence between a generated SQL result set and ground truth.

    Score from 0.0 to 1.0:
    1.0 — Semantically identical (same values; ordering or column-name differences are fine)
    0.75 — Mostly equivalent: minor differences such as rounding, one extra/missing row
    0.5 — Partially correct: right structure but meaningful gaps
    0.25 — Marginally related: correct shape but mostly wrong values
    0.0 — Completely wrong, one query errored, or results are unrelated

    Respond with ONLY a JSON object: {"score": <float>, "reason": "<one sentence>"}"""

    ground_truth_sql: str = dspy.InputField()
    ground_truth_result: str = dspy.InputField(desc="First 10 rows of ground truth result set")
    generated_sql: str = dspy.InputField()
    generated_result: str = dspy.InputField(desc="First 10 rows of generated result set")
    judgment: str = dspy.OutputField(desc='JSON {"score": float, "reason": str}')


class RelevanceJudgeSignature(dspy.Signature):
    """Score whether a generated SQL answer semantically addresses the user's question.

    Score from 0.0 to 1.0:
    1.0 — Perfectly answers the question
    0.75 — Mostly correct, minor gap
    0.5 — Partially answers but missing key aspect
    0.25 — Tangentially related but mostly wrong
    0.0 — Completely wrong or irrelevant

    Respond with ONLY a JSON object: {"score": <float>, "reason": "<one sentence>"}"""

    question: str = dspy.InputField()
    generated_sql: str = dspy.InputField()
    query_result: str = dspy.InputField(desc="First 5 rows of query result")
    judgment: str = dspy.OutputField(desc='JSON {"score": float, "reason": str}')


# ── DSPy modules ──────────────────────────────────────────────────────────────

class PlannerModule(dspy.Module):
    def __init__(self):
        self.predict = dspy.ChainOfThought(PlanSignature)

    def forward(self, question: str, db_schema: str) -> dspy.Prediction:
        return self.predict(question=question, db_schema=db_schema)


class SQLGeneratorModule(dspy.Module):
    def __init__(self):
        self.predict = dspy.ChainOfThought(SQLGenSignature)

    def forward(self, question: str, plan: str, db_schema: str) -> dspy.Prediction:
        return self.predict(question=question, plan=plan, db_schema=db_schema)


class TextToSQLPipeline(dspy.Module):
    """End-to-end planner → SQL generator, optimized jointly."""

    def __init__(self):
        self.planner = PlannerModule()
        self.sql_gen = SQLGeneratorModule()

    def forward(self, question: str, db_schema: str) -> dspy.Prediction:
        plan_pred = self.planner(question=question, db_schema=db_schema)
        sql_pred = self.sql_gen(question=question, plan=plan_pred.plan, db_schema=db_schema)
        return dspy.Prediction(plan=plan_pred.plan, sql=sql_pred.sql)


class AccuracyJudgeModule(dspy.Module):
    def __init__(self):
        self.predict = dspy.Predict(AccuracyJudgeSignature)

    def forward(self, ground_truth_sql, ground_truth_result, generated_sql, generated_result):
        return self.predict(
            ground_truth_sql=ground_truth_sql,
            ground_truth_result=ground_truth_result,
            generated_sql=generated_sql,
            generated_result=generated_result,
        )


class RelevanceJudgeModule(dspy.Module):
    def __init__(self):
        self.predict = dspy.Predict(RelevanceJudgeSignature)

    def forward(self, question, generated_sql, query_result):
        return self.predict(question=question, generated_sql=generated_sql, query_result=query_result)


# ── Dataset loading ────────────────────────────────────────────────────────────

def load_trainset(max_examples: int = 20) -> list[dspy.Example]:
    if not GOLDEN_DATASET_PATH.exists():
        print("Golden dataset not found — generating...")
        build_golden_dataset()

    data = json.loads(GOLDEN_DATASET_PATH.read_text())
    examples = []
    for item in data[:max_examples]:
        question = item["question"]
        if USE_SCHEMA_RETRIEVAL:
            schema, _ = retrieve_schema(question)
        else:
            schema = get_schema_str()

        examples.append(
            dspy.Example(
                question=question,
                db_schema=schema,
                ground_truth_sql=item["ground_truth_sql"],
            ).with_inputs("question", "db_schema")
        )

    print(f"Loaded {len(examples)} training examples")
    return examples


# ── Metrics ────────────────────────────────────────────────────────────────────

def pipeline_metric(example: dspy.Example, pred: dspy.Prediction, trace=None) -> float:
    """End-to-end execution accuracy: generated SQL vs ground truth SQL."""
    try:
        result = execution_accuracy(pred.sql.strip(), example.ground_truth_sql.strip())
        return result["score"]
    except Exception:
        return 0.0


def judge_metric(example: dspy.Example, pred: dspy.Prediction, trace=None) -> float:
    """Judge output metric: parse JSON and compare score to ground-truth label."""
    try:
        parsed = json.loads(re.search(r'\{.*\}', pred.judgment, re.DOTALL).group())
        predicted_score = float(parsed["score"])
        expected_score = float(example.expected_score)
        return 1.0 if abs(predicted_score - expected_score) <= 0.25 else 0.0
    except Exception:
        return 0.0


# ── Optimization ──────────────────────────────────────────────────────────────

def optimize_pipeline(
    trainset: list[dspy.Example],
    output_dir: Path,
    optimizer_name: str = "mipro",
) -> TextToSQLPipeline:
    """Jointly optimize the planner → SQL pipeline end-to-end."""
    print(f"\nOptimizing TextToSQLPipeline with {optimizer_name}...")

    pipeline = TextToSQLPipeline()

    if optimizer_name == "mipro":
        optimizer = MIPROv2(
            metric=pipeline_metric,
            auto="light",
            num_threads=1,   # serialize to avoid burst rate-limit failures
        )
        optimized = optimizer.compile(
            pipeline,
            trainset=trainset,
            requires_permission_to_run=False,
        )
    else:
        optimizer = BootstrapFewShot(metric=pipeline_metric, max_bootstrapped_demos=4)
        optimized = optimizer.compile(pipeline, trainset=trainset)

    save_path = output_dir / "pipeline.json"
    optimized.save(str(save_path))
    print(f"Saved → {save_path}")
    extract_prompts(optimized, output_dir)
    return optimized


def extract_prompts(pipeline: "TextToSQLPipeline", output_dir: Path) -> None:
    """Write instructions + bootstrapped demos to extracted.json for chat() use."""
    def _demos(predictor) -> list[dict]:
        state = predictor.dump_state()
        return [
            {k: v for k, v in d.items() if k not in ("db_schema", "augmented", "reasoning")}
            for d in state.get("demos", [])
            if d.get("augmented")
        ]

    planner_pred = pipeline.planner.predict.predict
    sql_gen_pred = pipeline.sql_gen.predict.predict

    out = {
        "planner": {
            "instructions": planner_pred.signature.instructions,
            "demos": _demos(planner_pred),
        },
        "sql_gen": {
            "instructions": sql_gen_pred.signature.instructions,
            "demos": _demos(sql_gen_pred),
        },
    }
    path = output_dir / "extracted.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"Extracted prompts → {path}")


def optimize_judges(
    trainset: list[dspy.Example],
    output_dir: Path,
) -> tuple[AccuracyJudgeModule, RelevanceJudgeModule]:
    """Optimize judge prompts using BootstrapFewShot.

    NOTE: This requires judge_trainset examples with an `expected_score` field.
    If none are available, judges are returned unoptimized.
    """
    print("\nOptimizing judge modules...")

    judge_examples = [ex for ex in trainset if hasattr(ex, "expected_score")]
    if not judge_examples:
        print("No labelled judge examples found — skipping judge optimization.")
        return AccuracyJudgeModule(), RelevanceJudgeModule()

    optimizer = BootstrapFewShot(metric=judge_metric, max_bootstrapped_demos=3)

    acc_judge = optimizer.compile(AccuracyJudgeModule(), trainset=judge_examples)
    acc_judge.save(str(output_dir / "accuracy_judge.json"))
    print(f"Saved → {output_dir / 'accuracy_judge.json'}")

    rel_judge = optimizer.compile(RelevanceJudgeModule(), trainset=judge_examples)
    rel_judge.save(str(output_dir / "relevance_judge.json"))
    print(f"Saved → {output_dir / 'relevance_judge.json'}")

    return acc_judge, rel_judge


# ── Entrypoint ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Optimize Text-to-SQL prompts with DSPy")
    parser.add_argument("--max-train", type=int, default=20, help="Max training examples (default 20)")
    parser.add_argument("--output-dir", type=Path, default=Path("optimized_prompts"))
    parser.add_argument(
        "--model",
        default=None,
        help="Full LiteLLM model string (e.g. anthropic/claude-sonnet-4-6, openai/gpt-4o). Prompted interactively if omitted.",
    )
    parser.add_argument("--api-key", default=None, help="API key for the chosen provider (overrides env)")
    parser.add_argument("--skip-judges", action="store_true", help="Skip judge prompt optimization")
    parser.add_argument(
        "--optimizer", choices=["mipro", "bootstrap"], default="mipro",
        help="mipro=MIPROv2 (better, slower); bootstrap=BootstrapFewShot (faster)"
    )
    args = parser.parse_args()

    if args.model:
        model = args.model
    else:
        _default = f"anthropic/{MODEL}"
        _prompt = (
            f"Model (LiteLLM format, e.g. anthropic/claude-sonnet-4-6, openai/gpt-4o,\n"
            f"       openrouter/google/gemini-2.5-pro) [default: {_default}]: "
        )
        _answer = input(_prompt).strip()
        model = _answer if _answer else _default

    args.output_dir.mkdir(exist_ok=True)

    print("Initializing environment...")
    init_db()
    try:
        build_schema_store()
    except Exception:
        pass

    configure_lm(model=model, api_key=args.api_key)

    trainset = load_trainset(max_examples=args.max_train)
    if not trainset:
        print("No training data available.")
        return

    optimized_pipeline = optimize_pipeline(trainset, args.output_dir, args.optimizer)

    if not args.skip_judges:
        optimize_judges(trainset, args.output_dir)

    print("\nDone. To apply optimized instructions:")
    print(f"  pipeline = TextToSQLPipeline()")
    print(f"  pipeline.load('{args.output_dir}/pipeline.json')")
    print(f"  # Extract planner instructions:")
    print(f"  print(pipeline.planner.predict.signature.instructions)")
    print(f"  # Extract SQL generator instructions:")
    print(f"  print(pipeline.sql_gen.predict.signature.instructions)")


if __name__ == "__main__":
    main()
