"""
Evaluation metrics:
1. sql_validity       — heuristic: does the SQL execute without error?
2. execution_accuracy — F1 heuristic with LLM-as-judge fallback below threshold
3. answer_relevance   — LLM-as-judge: does the answer semantically address intent?
4. schema_recall      — heuristic: did the model use all tables required by the ground truth?

Each metric is exposed both as a plain function (for unit tests / ad-hoc use)
and as an opik BaseMetric subclass (for use with opik.evaluation.evaluate()).
"""
import json
import re
import anthropic
import sys
from pathlib import Path
from typing import Any, TypedDict
import sqlglot
import sqlglot.expressions as exp
from opik.evaluation.metrics import base_metric, score_result

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, MODEL_JUDGE, OPIK_PROJECT_NAME, THRESHOLD_EXECUTION_ACCURACY
from db.database import run_query

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ── 1. SQL Validity ──────────────────────────────────────────────────────────

def sql_validity(sql: str) -> bool:
    """Returns True if the SQL executes without error."""
    if not sql or not sql.strip().upper().startswith("SELECT"):
        return False
    _, error = run_query(sql)
    return error is None


class SqlValidityMetric(base_metric.BaseMetric):
    def __init__(self) -> None:
        super().__init__(name="sql_validity", project_name=OPIK_PROJECT_NAME)

    def score(self, output: str, **kwargs: Any) -> score_result.ScoreResult:
        value = float(sql_validity(output))
        return score_result.ScoreResult(
            name=self.name,
            value=value,
            reason="valid" if value else "SQL did not execute or is not a SELECT",
        )


# ── 2. Execution Accuracy ────────────────────────────────────────────────────

class ExecutionAccuracyResult(TypedDict):
    score: float
    gen_rows: list[dict] | None
    gt_rows: list[dict] | None
    norm_gen_rows: frozenset | None
    norm_gt_rows: frozenset | None
    gen_error: str | None
    gt_error: str | None
    accu_judge_reason: str | None


ACCURACY_JUDGE_SYSTEM = """You are an evaluation judge for a Text-to-SQL system.
Compare the result set of a generated SQL query against the ground truth result set and score their semantic equivalence.

Score from 0.0 to 1.0:
1.0 — Semantically identical (same values; ordering or column-name differences are fine)
0.75 — Mostly equivalent: minor differences such as a rounding gap, one extra/missing row, or an extra metadata column
0.5 — Partially correct: right structure but meaningful gaps (wrong aggregation, missing join, subset of rows)
0.25 — Marginally related: correct shape but mostly wrong values or row count is far off
0.0 — Completely wrong, one query errored, or results are unrelated

Respond with ONLY a JSON object: {"score": <float>, "reason": "<one sentence>"}"""


def _normalize_column_name(col: str) -> str:
    """
    Normalize column name for alias-aware comparison.
    Converts to lowercase and removes underscores, hyphens, spaces.
    E.g., 'total_high_risk_amount' → 'totalhighriskamount'
    """
    return re.sub(r'[_\-\s]+', '', col.lower())


def _f1_score(gen_rows: list[dict], gt_rows: list[dict]) -> float:
    """
    Row-level F1 with column-name awareness and aliasing handling.
    
    Normalizes column names to catch semantic aliases (e.g., total_high_risk vs total-high-risk).
    Compares rows by (normalized_column_name, value) pairs.
    """
    def normalize_row(row: dict) -> dict:
        """Convert row: keys → normalized column names, values → strings."""
        return {_normalize_column_name(k): str(v) for k, v in row.items()}

    gen_norm = [normalize_row(row) for row in gen_rows]
    gt_norm = [normalize_row(row) for row in gt_rows]

    # Match rows: ground truth pool with removals to avoid double-counting
    gt_pool = list(gt_norm)
    matched = 0
    for gen_row in gen_norm:
        # Find exact match in gt_pool (normalized columns + values)
        for i, gt_row in enumerate(gt_pool):
            if gen_row == gt_row:
                gt_pool.pop(i)
                matched += 1
                break

    precision = matched / len(gen_norm) if gen_norm else 0.0
    recall    = matched / len(gt_norm)  if gt_norm  else 0.0
    if precision + recall == 0:
        return 0.0, gen_norm, gt_norm
    return 2 * precision * recall / (precision + recall), gen_norm, gt_norm


def _llm_accuracy_judge(generated_sql: str, ground_truth_sql: str,
                         gen_rows: list[dict], gt_rows: list[dict]) -> tuple[float, str | None]:
    """LLM-as-judge fallback for borderline execution accuracy scores."""
    gen_preview = str(gen_rows[:10])
    gt_preview  = str(gt_rows[:10])

    response = client.messages.create(
        model=MODEL_JUDGE,
        max_tokens=150,
        system=ACCURACY_JUDGE_SYSTEM,
        messages=[{
            "role": "user",
            "content": (
                f"Ground truth SQL:\n{ground_truth_sql}\n"
                f"Ground truth result ({len(gt_rows)} rows, first 10):\n{gt_preview}\n\n"
                f"Generated SQL:\n{generated_sql}\n"
                f"Generated result ({len(gen_rows)} rows, first 10):\n{gen_preview}"
            ),
        }],
    )

    text = response.content[0].text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            return float(parsed["score"]), parsed.get("reason")
        except Exception:
            pass
    return 0.0, None


def execution_accuracy(generated_sql: str, ground_truth_sql: str) -> ExecutionAccuracyResult:
    """
    Primary: row-level F1 with value-only normalisation (column-alias agnostic).
    Fallback: LLM-as-judge when the F1 score is below THRESHOLD_EXECUTION_ACCURACY.
    """
    gen_rows, gen_err = run_query(generated_sql)
    gt_rows,  gt_err  = run_query(ground_truth_sql)

    result: ExecutionAccuracyResult = {
        "score": 0.0,
        "gen_rows": gen_rows,
        "gt_rows": gt_rows,
        "norm_gen_rows": None,
        "norm_gt_rows": None,
        "gen_error": gen_err,
        "gt_error": gt_err,
        "accu_judge_reason": None,
    }

    if gen_err or gt_err:
        return result  # hard failure: score stays 0.0, no judge needed

    if not gen_rows and not gt_rows:
        result["score"] = 1.0
        return result

    score, result["norm_gen_rows"], result["norm_gt_rows"] = _f1_score(gen_rows, gt_rows)
    if score < THRESHOLD_EXECUTION_ACCURACY:
        score, result["accu_judge_reason"] = _llm_accuracy_judge(
            generated_sql, ground_truth_sql, gen_rows, gt_rows
        )

    result["score"] = score
    return result


class ExecutionAccuracyMetric(base_metric.BaseMetric):
    def __init__(self) -> None:
        super().__init__(name="execution_accuracy", project_name=OPIK_PROJECT_NAME)

    def score(self, output: str, ground_truth_sql: str, **kwargs: Any) -> score_result.ScoreResult:
        result = execution_accuracy(output, ground_truth_sql)
        return score_result.ScoreResult(
            name=self.name,
            value=result["score"],
            reason=result["accu_judge_reason"],
            metadata={
                "gen_rows": result["gen_rows"],
                "gt_rows": result["gt_rows"],
                "norm_gen_rows": result["norm_gen_rows"],
                "norm_gt_rows": result["norm_gt_rows"],
                "gen_error": result["gen_error"],
                "gt_error": result["gt_error"],
            },
        )


# ── 3. Answer Relevance ──────────────────────────────────────────────────────

RELEVANCE_SYSTEM = """You are an evaluation judge for a Text-to-SQL system.
Score whether the generated SQL answer semantically addresses the user's question.

Score from 0.0 to 1.0:
1.0 — Perfectly answers the question
0.75 — Mostly correct, minor gap
0.5 — Partially answers but missing key aspect
0.25 — Tangentially related but mostly wrong
0.0 — Completely wrong or irrelevant

Respond with ONLY a JSON object: {"score": <float>, "reason": "<one sentence>"}"""


def answer_relevance(
    question: str, generated_sql: str, query_result: list[dict]
) -> tuple[float, str | None]:
    """LLM-as-judge: returns score and reason for how well SQL + result address intent."""
    result_preview = str(query_result[:5]) if query_result else "No results returned"

    response = client.messages.create(
        model=MODEL_JUDGE,
        max_tokens=150,
        system=RELEVANCE_SYSTEM,
        messages=[{
            "role": "user",
            "content": (
                f"User question: {question}\n\n"
                f"Generated SQL:\n{generated_sql}\n\n"
                f"Query result (first 5 rows): {result_preview}"
            ),
        }],
    )

    text = response.content[0].text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            return float(parsed["score"]), parsed.get("reason")
        except Exception:
            pass
    return 0.0, None


class AnswerRelevanceMetric(base_metric.BaseMetric):
    def __init__(self) -> None:
        super().__init__(name="answer_relevance", project_name=OPIK_PROJECT_NAME)

    def score(self, question: str, output: str, query_result: list[dict], **kwargs: Any) -> score_result.ScoreResult:
        value, reason = answer_relevance(question, output, query_result)
        return score_result.ScoreResult(
            name=self.name,
            value=value,
            reason=reason,
        )


# ── 4. Schema Recall ─────────────────────────────────────────────────────────

def schema_recall(generated_sql: str, needed_tables: list[str]) -> float:
    """
    Proxy metric (pre-vector-DB): extracts tables used in generated_sql and
    measures coverage of needed_tables derived from ground_truth_sql.

    Returns 1.0 when needed_tables is empty (nothing required → nothing missing).
    When the vector DB retrieval layer is added, swap generated_sql for the
    list of tables actually returned by the retriever.
    """
    if not needed_tables:
        return 1.0

    try:
        parsed = sqlglot.parse_one(generated_sql, dialect="sqlite")
        used = {t.name.lower() for t in parsed.find_all(exp.Table) if t.name}
    except sqlglot.errors.ParseError:
        return 0.0

    needed = {t.lower() for t in needed_tables}
    return len(used & needed) / len(needed)


class SchemaRecallMetric(base_metric.BaseMetric):
    def __init__(self) -> None:
        super().__init__(name="schema_recall", project_name=OPIK_PROJECT_NAME)

    def score(self, output: str, needed_tables: list[str] | None = None, **kwargs: Any) -> score_result.ScoreResult:
        value = schema_recall(output, needed_tables or [])
        return score_result.ScoreResult(name=self.name, value=value)
