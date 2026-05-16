"""
Phase 2: Automated Evaluation Pipeline with OPIK integration.
Run: python evaluation/pipeline.py
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import opik
from opik import track
from config import (
    OPIK_API_KEY,
    OPIK_PROJECT_NAME,
    GOLDEN_DATASET_PATH,
    EVAL_RESULTS_PATH,
    THRESHOLD_SQL_VALIDITY,
    THRESHOLD_EXECUTION_ACCURACY,
    THRESHOLD_ANSWER_RELEVANCE,
)
from agents.graph import run_query_pipeline
from evaluation.metrics import sql_validity, execution_accuracy, answer_relevance

opik.configure(api_key=OPIK_API_KEY, use_local=False)
opik_client = opik.Opik(project_name=OPIK_PROJECT_NAME)


@track(project_name=OPIK_PROJECT_NAME)
def evaluate_single(entry: dict) -> dict:
    """Run one golden dataset entry through the pipeline and score it."""
    question = entry["question"]
    ground_truth_sql = entry["ground_truth_sql"]

    start = time.time()
    result = run_query_pipeline(question)
    latency_ms = int((time.time() - start) * 1000)

    gen_sql = result.get("generated_sql", "")
    gov_result = result.get("governance_result", "")
    query_result = result.get("query_result", [])

    validity = sql_validity(gen_sql)
    accuracy = execution_accuracy(gen_sql, ground_truth_sql)
    relevance = answer_relevance(question, gen_sql, query_result)

    return {
        "id": entry["id"],
        "question": question,
        "ground_truth_sql": ground_truth_sql,
        "generated_sql": gen_sql,
        "governance_result": gov_result,
        "sql_validity": validity,
        "execution_accuracy": accuracy,
        "answer_relevance": relevance,
        "complexity": entry.get("complexity"),
        "operations": entry.get("operations", []),
        "risk_level": entry.get("risk_level"),
        "domain": entry.get("domain"),
        "latency_ms": latency_ms,
    }


def compute_gate(results: list[dict]) -> dict:
    n = len(results)
    validity_score = sum(r["sql_validity"] for r in results) / n
    accuracy_score = sum(r["execution_accuracy"] for r in results) / n
    relevance_score = sum(r["answer_relevance"] for r in results) / n

    gate = {
        "sql_validity": {"score": round(validity_score, 4), "threshold": THRESHOLD_SQL_VALIDITY, "pass": validity_score >= THRESHOLD_SQL_VALIDITY},
        "execution_accuracy": {"score": round(accuracy_score, 4), "threshold": THRESHOLD_EXECUTION_ACCURACY, "pass": accuracy_score >= THRESHOLD_EXECUTION_ACCURACY},
        "answer_relevance": {"score": round(relevance_score, 4), "threshold": THRESHOLD_ANSWER_RELEVANCE, "pass": relevance_score >= THRESHOLD_ANSWER_RELEVANCE},
    }
    gate["ship"] = all(v["pass"] for v in gate.values())
    return gate


def run_evaluation(max_entries: int | None = None) -> dict:
    if not GOLDEN_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Golden dataset not found at {GOLDEN_DATASET_PATH}. "
            "Run: python dataset/generate_dataset.py"
        )

    dataset = json.loads(GOLDEN_DATASET_PATH.read_text())
    if max_entries:
        dataset = dataset[:max_entries]

    print(f"Running evaluation on {len(dataset)} entries...")

    results = []
    for i, entry in enumerate(dataset, 1):
        print(f"  [{i}/{len(dataset)}] {entry['id']}: {entry['question'][:55]}...")
        try:
            scored = evaluate_single(entry)
            results.append(scored)
            validity_str = "PASS" if scored["sql_validity"] else "FAIL"
            acc_str = f"{scored['execution_accuracy']:.2f}"
            rel_str = f"{scored['answer_relevance']:.2f}"
            print(f"    validity={validity_str} accuracy={acc_str} relevance={rel_str}")
        except Exception as e:
            print(f"    ERROR: {e}")

    gate = compute_gate(results)

    output = {
        "run_at": datetime.utcnow().isoformat(),
        "total_entries": len(results),
        "gate": gate,
        "results": results,
    }

    EVAL_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_RESULTS_PATH.write_text(json.dumps(output, indent=2))

    _print_scorecard(gate)
    return output


def _print_scorecard(gate: dict) -> None:
    print("\n" + "=" * 50)
    print("  LAUNCH GATE SCORECARD")
    print("=" * 50)
    metrics = ["sql_validity", "execution_accuracy", "answer_relevance"]
    labels = ["SQL Validity      ", "Execution Accuracy", "Answer Relevance  "]
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
