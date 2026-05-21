import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MODEL
from agents.llm import chat
from agents.prompt_store import get_sql_gen_prompt

_INSTRUCTIONS = """You are a SQL generation assistant for an insurance analytics platform.
You will receive a query plan and must produce a single valid SQLite SELECT statement.

STRICT RULES:
- Only generate SELECT statements. Never use DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, or CREATE.
- Use SQLite-compatible syntax: strftime(), julianday(), date() for date operations.
- Always use table aliases for readability.
- Return ONLY the raw SQL query — no markdown, no explanation, no code fences.
- If the question cannot be answered with the available schema, return: SELECT 'Query out of scope' as message"""


def extract_sql(text: str) -> str:
    text = text.strip()
    if "```" in text:
        match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return text


def sql_generator_node(state: dict) -> dict:
    schema   = state.get("retrieved_schema", "")
    model    = state.get("model") or MODEL
    api_key  = state.get("llm_api_key") or None
    backend  = state.get("llm_backend") or None
    question = state["user_question"]
    plan     = state["plan"]

    # Planner already ran the full DSPy pipeline and stored generated_sql.
    if state.get("_dspy_ran"):
        state["generated_sql"] = extract_sql(state.get("generated_sql", ""))
        return state

    system_prompt = get_sql_gen_prompt(schema) or f"{_INSTRUCTIONS}\n\nDatabase schema:\n{schema}"
    user_msg = (
        f"Original question: {question}\n\n"
        f"Query plan:\n{plan}\n\n"
        "Generate the SQLite SELECT query:"
    )
    state["generated_sql"] = extract_sql(
        chat(
            model,
            system_prompt,
            user_msg,
            max_tokens=600,
            cache_system=True,
            api_key=api_key,
            backend=backend,
        )
    )
    return state
