import re
import anthropic
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

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
    # Reuse the schema retrieved by the planner — no second vector lookup needed
    schema = state.get("retrieved_schema", "")
    system_prompt = f"{_INSTRUCTIONS}\n\nDatabase schema:\n{schema}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=[{
            "role": "user",
            "content": (
                f"Original question: {state['user_question']}\n\n"
                f"Query plan:\n{state['plan']}\n\n"
                "Generate the SQLite SELECT query:"
            ),
        }],
    )
    state["generated_sql"] = extract_sql(response.content[0].text)
    return state
