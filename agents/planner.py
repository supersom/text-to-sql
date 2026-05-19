import anthropic
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, MODEL, USE_SCHEMA_RETRIEVAL
from db.database import get_schema_str, get_all_table_names
from db.schema_store import retrieve_schema

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

_INSTRUCTIONS = """You are a SQL planning assistant for an insurance analytics platform.
Given a natural language question and the relevant database schema, produce a structured query plan.

Your plan must include:
1. TABLES: which tables are needed
2. JOINS: which tables to join and on what keys
3. FILTERS: WHERE conditions (values, date ranges, status filters)
4. AGGREGATIONS: COUNT, SUM, AVG, GROUP BY, ORDER BY, LIMIT
5. INTENT: one sentence describing what the user wants

Be concise. Output plain text, not JSON or markdown."""


def planner_node(state: dict) -> dict:
    question = state["user_question"]

    if USE_SCHEMA_RETRIEVAL:
        schema, retrieved_tables = retrieve_schema(question)
    else:
        schema, retrieved_tables = get_schema_str(), get_all_table_names()

    state["retrieved_schema"] = schema
    state["retrieved_tables"] = retrieved_tables

    system_prompt = f"{_INSTRUCTIONS}\n\nDatabase schema:\n{schema}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": f"Question: {question}"}],
    )
    state["plan"] = response.content[0].text.strip()
    return state
