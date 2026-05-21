"""
Runtime loader for optimized DSPy prompts.

  get_pipeline()            — load the saved TextToSQLPipeline for direct DSPy use
                              (API backends only); returns None if unavailable.
  get_planner_prompt(schema) — return a formatted system-prompt string built from
  get_sql_gen_prompt(schema)   optimized instructions + demos, for use with chat().
                              Returns None when no extracted prompts exist, so callers
                              can fall back to the hard-coded _INSTRUCTIONS.

Both loaders are lazy and cached; the files are read once per process.
"""
import json
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_PIPELINE_PATH  = _ROOT / "optimized_prompts" / "pipeline.json"
_EXTRACTED_PATH = _ROOT / "optimized_prompts" / "extracted.json"

_pipeline         = None
_pipeline_checked = False
_extracted        = None
_extracted_checked = False


def get_pipeline():
    """Return the loaded TextToSQLPipeline, or None if unavailable."""
    global _pipeline, _pipeline_checked
    if _pipeline_checked:
        return _pipeline
    _pipeline_checked = True
    if not _PIPELINE_PATH.exists():
        return None
    try:
        import dspy                               # noqa: F401 — optional dep
        from optimize_prompts import TextToSQLPipeline
        p = TextToSQLPipeline()
        p.load(str(_PIPELINE_PATH))
        _pipeline = p
    except Exception:
        pass
    return _pipeline


def _load_extracted() -> dict | None:
    global _extracted, _extracted_checked
    if _extracted_checked:
        return _extracted
    _extracted_checked = True
    if _EXTRACTED_PATH.exists():
        try:
            _extracted = json.loads(_EXTRACTED_PATH.read_text())
        except Exception:
            pass
    return _extracted


def get_planner_prompt(schema: str) -> str | None:
    """Optimized planner system prompt (instructions + demos) for chat()."""
    data = _load_extracted()
    if not data:
        return None
    p = data.get("planner", {})
    return _build_prompt(p.get("instructions", ""), p.get("demos", []), schema, "plan")


def get_sql_gen_prompt(schema: str) -> str | None:
    """Optimized SQL generator system prompt (instructions + demos) for chat()."""
    data = _load_extracted()
    if not data:
        return None
    s = data.get("sql_gen", {})
    return _build_prompt(s.get("instructions", ""), s.get("demos", []), schema, "sql")


def _build_prompt(instructions: str, demos: list, schema: str, output_field: str) -> str | None:
    if not instructions:
        return None
    parts = [instructions, f"\nDatabase schema:\n{schema}"]
    if demos:
        parts.append("\n--- Examples ---")
        for d in demos:
            if output_field == "plan":
                parts.append(
                    f"\nQuestion: {d.get('question', '')}\n"
                    f"Plan: {d.get('plan', '')}"
                )
            else:
                parts.append(
                    f"\nQuestion: {d.get('question', '')}\n"
                    f"Plan: {d.get('plan', '')}\n"
                    f"SQL: {d.get('sql', '')}"
                )
    return "\n".join(parts)
