"""
Evaluation pipeline using the standard opik.evaluation.evaluate() form.
Run: python evaluation/pipeline.py
"""
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import opik
from opik.evaluation import evaluate
from opik.evaluation.evaluation_result import EvaluationResult
from config import (
    OPIK_API_KEY,
    OPIK_PROJECT_NAME,
    MODEL,
    MODEL_JUDGE,
    TASK_THREADS,
    GOLDEN_DATASET_PATH,
    EVAL_RESULTS_PATH,
    THRESHOLD_SQL_VALIDITY,
    THRESHOLD_EXECUTION_ACCURACY,
    THRESHOLD_ANSWER_RELEVANCE,
    THRESHOLD_SCHEMA_RECALL,
)
from agents.graph import run_query_pipeline
from evaluation.metrics import (
    SqlValidityMetric,
    ExecutionAccuracyMetric,
    AnswerRelevanceMetric,
    SchemaRecallMetric,
)

opik.configure(api_key=OPIK_API_KEY, use_local=False)
opik_client = opik.Opik()

DATASET_NAME = "text-to-sql-golden-dataset"


# opik.evaluate() calls task(dataset_item) — it controls the call site and expects that exact
# signature. We can't add api_key as a parameter because opik would never pass it. The closure
# captures api_key in scope while the inner function keeps the signature opik expects.
def make_evaluation_task(api_key: str | None = None, backend: str | None = None):
    def evaluation_task(dataset_item: dict) -> dict:
        result = run_query_pipeline(dataset_item["question"], api_key=api_key, backend=backend)
        return {
            "output": result.get("generated_sql", ""),
            "governance_result": result.get("governance_result", ""),
            "query_result": result.get("query_result", []),
            "retrieved_tables": result.get("retrieved_tables", []),
        }
    return evaluation_task


def sync_dataset(dataset_items: list[dict]) -> opik.Dataset:
    """Upload golden dataset items to OPIK, creating a new dataset version.

    Renames 'id' to 'item_id' to avoid collision with DatasetItem's internal
    id field, which must be a UUID.
    """
    dataset = opik_client.get_or_create_dataset(
        DATASET_NAME,
        description="Text-to-SQL golden evaluation dataset",
    )
    items = [{"item_id": item.get("id"), **{k: v for k, v in item.items() if k != "id"}}
             for item in dataset_items]
    dataset.insert(items)
    return dataset


def compute_gate(eval_result: EvaluationResult) -> dict:
    scores: dict[str, list[float]] = {
        "sql_validity": [],
        "execution_accuracy": [],
        "answer_relevance": [],
        "schema_recall": [],
    }

    for test_result in eval_result.test_results:
        for sr in test_result.score_results:
            if sr.name in scores and not sr.scoring_failed:
                scores[sr.name].append(sr.value)

    thresholds = {
        "sql_validity": THRESHOLD_SQL_VALIDITY,
        "execution_accuracy": THRESHOLD_EXECUTION_ACCURACY,
        "answer_relevance": THRESHOLD_ANSWER_RELEVANCE,
        "schema_recall": THRESHOLD_SCHEMA_RECALL,
    }

    gate = {}
    for name, threshold in thresholds.items():
        values = scores[name]
        avg = sum(values) / len(values) if values else 0.0
        gate[name] = {"score": round(avg, 4), "threshold": threshold, "pass": avg >= threshold}

    gate["ship"] = all(v["pass"] for v in gate.values())
    return gate


def _build_results_json(eval_result: EvaluationResult) -> list[dict]:
    """Reconstruct the per-entry results list for the Streamlit dashboard."""
    rows = []
    for tr in eval_result.test_results:
        item = tr.test_case.dataset_item_content
        task_out = tr.test_case.task_output
        score_map = {sr.name: sr for sr in tr.score_results}

        exec_sr = score_map.get("execution_accuracy")
        meta = exec_sr.metadata or {} if exec_sr else {}

        rows.append({
            "id": item.get("item_id"),
            "question": item.get("question"),
            "ground_truth_sql": item.get("ground_truth_sql"),
            "generated_sql": task_out.get("output"),
            "governance_result": task_out.get("governance_result"),
            "retrieved_tables": task_out.get("retrieved_tables", []),
            "needed_tables": item.get("needed_tables", []),
            "sql_validity": score_map["sql_validity"].value if "sql_validity" in score_map else None,
            "execution_accuracy": exec_sr.value if exec_sr else None,
            "accu_judge_reason": exec_sr.reason if exec_sr else None,
            "gen_rows": meta.get("gen_rows"),
            "gt_rows": meta.get("gt_rows"),
            "gen_error": meta.get("gen_error"),
            "gt_error": meta.get("gt_error"),
            "answer_relevance": score_map["answer_relevance"].value if "answer_relevance" in score_map else None,
            "schema_recall": score_map["schema_recall"].value if "schema_recall" in score_map else None,
            "complexity": item.get("complexity"),
            "operations": item.get("operations", []),
            "risk_level": item.get("risk_level"),
            "domain": item.get("domain"),
            "latency_ms": int(tr.task_execution_time * 1000) if tr.task_execution_time else None,
        })
    return rows


def run_evaluation(max_entries: int | None = None, api_key: str | None = None, backend: str | None = None) -> dict:
    if not GOLDEN_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Golden dataset not found at {GOLDEN_DATASET_PATH}. "
            "Run: python dataset/generate_dataset.py"
        )

    dataset_items = json.loads(GOLDEN_DATASET_PATH.read_text())
    if max_entries:
        dataset_items = dataset_items[:max_entries]

    dataset = sync_dataset(dataset_items)

    eval_result = evaluate(
        dataset=dataset,
        task=make_evaluation_task(api_key=api_key, backend=backend),
        scoring_metrics=[
            SqlValidityMetric(),
            ExecutionAccuracyMetric(api_key=api_key, backend=backend),
            AnswerRelevanceMetric(api_key=api_key, backend=backend),
            SchemaRecallMetric(),
        ],
        experiment_name_prefix="text-to-sql-eval",
        project_name=OPIK_PROJECT_NAME,
        experiment_config={"model": MODEL, "model_judge": MODEL_JUDGE},
        nb_samples=max_entries,
        verbose=1,
        task_threads=int(TASK_THREADS),
    )

    gate = compute_gate(eval_result)

    output = {
        "run_at": datetime.utcnow().isoformat(),
        "total_entries": len(eval_result.test_results),
        "experiment_id": eval_result.experiment_id,
        "experiment_url": eval_result.experiment_url,
        "gate": gate,
        "results": _build_results_json(eval_result),
    }

    EVAL_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_RESULTS_PATH.write_text(json.dumps(output, indent=2))

    _print_scorecard(gate)
    return output


def _print_scorecard(gate: dict) -> None:
    print("\n" + "=" * 50)
    print("  LAUNCH GATE SCORECARD")
    print("=" * 50)
    metrics = ["sql_validity", "execution_accuracy", "answer_relevance", "schema_recall"]
    labels = ["SQL Validity      ", "Execution Accuracy", "Answer Relevance  ", "Schema Recall     "]
    for m, label in zip(metrics, labels):
        g = gate[m]
        status = "PASS ✓" if g["pass"] else "FAIL ✗"
        print(f"  {label}: {g['score']:.1%}  (threshold: {g['threshold']:.0%})  [{status}]")
    print("=" * 50)
    decision = "SHIP ✓" if gate["ship"] else "NO-SHIP ✗"
    print(f"  Decision: {decision}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=None, help="Limit entries for quick run")
    args = parser.parse_args()
    run_evaluation(max_entries=args.max)
