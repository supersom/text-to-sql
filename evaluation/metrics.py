"""
Three mandatory evaluation metrics:
1. sql_validity     — heuristic: does the SQL execute without error?
2. execution_accuracy — heuristic: does the result set match ground truth?
3. answer_relevance   — LLM-as-judge: does the answer semantically address intent?
"""
import anthropic
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, MODEL_JUDGE
from db.database import run_query

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def sql_validity(sql: str) -> bool:
    """Returns True if the SQL executes without error."""
    if not sql or not sql.strip().upper().startswith("SELECT"):
        return False
    _, error = run_query(sql)
    return error is None


def execution_accuracy(generated_sql: str, ground_truth_sql: str) -> float:
    """
    Returns 1.0 if result sets match exactly, 0.0 otherwise.
    Compares rows as frozensets to ignore ordering.
    """
    gen_rows, gen_err = run_query(generated_sql)
    gt_rows, gt_err = run_query(ground_truth_sql)

    if gen_err or gt_err:
        return 0.0
    if not gen_rows and not gt_rows:
        return 1.0

    def normalize(rows: list[dict]) -> frozenset:
        return frozenset(
            frozenset((k, str(v)) for k, v in row.items())
            for row in rows
        )

    return 1.0 if normalize(gen_rows) == normalize(gt_rows) else 0.0


RELEVANCE_SYSTEM = """You are an evaluation judge for a Text-to-SQL system.
Score whether the generated SQL answer semantically addresses the user's question.

Score from 0.0 to 1.0:
1.0 — Perfectly answers the question
0.75 — Mostly correct, minor gap
0.5 — Partially answers but missing key aspect
0.25 — Tangentially related but mostly wrong
0.0 — Completely wrong or irrelevant

Respond with ONLY a JSON object: {"score": <float>, "reason": "<one sentence>"}"""


def answer_relevance(question: str, generated_sql: str, query_result: list[dict]) -> float:
    """LLM-as-judge: scores how well the SQL + result addresses the user's intent."""
    result_preview = str(query_result[:5]) if query_result else "No results returned"

    response = client.messages.create(
        model=MODEL_JUDGE,
        max_tokens=150,
        system=RELEVANCE_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": (
                    f"User question: {question}\n\n"
                    f"Generated SQL:\n{generated_sql}\n\n"
                    f"Query result (first 5 rows): {result_preview}"
                ),
            }
        ],
    )

    import json, re
    text = response.content[0].text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return float(json.loads(match.group())["score"])
        except Exception:
            pass
    return 0.0
