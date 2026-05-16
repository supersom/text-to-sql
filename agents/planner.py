import anthropic
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, MODEL
from db.database import get_schema_str

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
SCHEMA = get_schema_str()

SYSTEM_PROMPT = f"""You are a SQL planning assistant for an insurance analytics platform.
Given a natural language question, analyze it and produce a structured query plan.

Database schema:
{SCHEMA}

Your plan must include:
1. TABLES: which tables are needed
2. JOINS: which tables to join and on what keys
3. FILTERS: WHERE conditions (values, date ranges, status filters)
4. AGGREGATIONS: COUNT, SUM, AVG, GROUP BY, ORDER BY, LIMIT
5. INTENT: one sentence describing what the user wants

Be concise. Output plain text, not JSON or markdown."""


def planner_node(state: dict) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Question: {state['user_question']}",
            }
        ],
    )
    state["plan"] = response.content[0].text.strip()
    return state
