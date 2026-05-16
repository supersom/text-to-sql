import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FORBIDDEN_SQL_KEYWORDS
from db.database import run_query


def governance_node(state: dict) -> dict:
    sql = state.get("generated_sql", "").strip()

    if not sql:
        state["governance_result"] = "BLOCKED: empty SQL"
        state["query_result"] = []
        state["answer"] = "No SQL was generated."
        return state

    # Check starts with SELECT
    first_token = sql.split()[0].upper() if sql.split() else ""
    if first_token != "SELECT":
        state["governance_result"] = f"BLOCKED: statement must start with SELECT, got '{first_token}'"
        state["query_result"] = []
        state["answer"] = "This query was blocked by the governance layer (non-SELECT statement)."
        return state

    # Check for forbidden keywords anywhere in the SQL
    sql_upper = sql.upper()
    for keyword in FORBIDDEN_SQL_KEYWORDS:
        # Use word boundary check to avoid false positives
        import re
        if re.search(rf"\b{keyword}\b", sql_upper):
            state["governance_result"] = f"BLOCKED: forbidden keyword '{keyword}' detected"
            state["query_result"] = []
            state["answer"] = f"This query was blocked by the governance layer (forbidden operation: {keyword})."
            return state

    # Execute the query
    rows, error = run_query(sql)
    if error:
        state["governance_result"] = f"SQL_ERROR: {error}"
        state["query_result"] = []
        state["answer"] = f"The generated SQL produced an error: {error}"
        return state

    state["governance_result"] = "PASSED"
    state["query_result"] = rows

    if not rows:
        state["answer"] = "The query executed successfully but returned no results."
    else:
        state["answer"] = f"Query returned {len(rows)} row(s)."

    return state
