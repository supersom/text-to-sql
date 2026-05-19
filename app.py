"""
Text-to-SQL — Streamlit UI
Run: streamlit run app.py
"""
import json
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from config import FEEDBACK_PATH, EVAL_RESULTS_PATH, SEED_QUERIES_PATH, KEY_FROM_UI, MODEL, MODEL_JUDGE
from db.database import init_db, run_query
from db.schema_store import build_schema_store, COLLECTION_NAME, _client
from agents.graph import run_query_pipeline

st.set_page_config(
    page_title="Text-to-SQL",
    page_icon="🔍",
    layout="wide",
)

# Ensure DB and schema vector store are initialized on first run
@st.cache_resource
def ensure_db():
    init_db()

@st.cache_resource
def ensure_schema_store():
    try:
        _client().get_collection(COLLECTION_NAME)
    except Exception:
        build_schema_store()

ensure_db()
ensure_schema_store()


def save_feedback(question: str, sql: str, result_count: int, thumbs_up: bool) -> None:
    feedback = []
    if FEEDBACK_PATH.exists():
        feedback = json.loads(FEEDBACK_PATH.read_text())
    feedback.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "question": question,
        "generated_sql": sql,
        "result_count": result_count,
        "positive": thumbs_up,
    })
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_PATH.write_text(json.dumps(feedback, indent=2))


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Text-to-SQL for Analytics")
    st.caption("NLP Query Interface — Text-to-SQL")
    st.markdown("---")
    st.markdown("**Quick examples:**")
    examples = [
        "How many high-risk claims are still open?",
        "Which adjuster handled the most claims?",
        "What is the total fraud savings from resolved fraud flags?",
        "Show claims over $50,000 that are under review",
        "What is the average time to resolve a claim?",
        "Which region has the most high-risk claims?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:20]}", use_container_width=True):
            st.session_state["question_input"] = ex
    st.markdown("---")

    if KEY_FROM_UI:
        st.markdown("**Configuration**")
        _KEY_HELP = (
            "API key for your chosen LLM provider.\n\n"
            "**Where to get one:**\n"
            "- **Anthropic** → console.anthropic.com/settings/keys\n"
            "- **OpenAI** → platform.openai.com/api-keys\n"
            "- **OpenRouter** → openrouter.ai/keys\n"
            "- **HuggingFace** → huggingface.co/settings/tokens\n\n"
            "Your key is never stored — this app is open source."
        )
        st.text_input("API Key", type="password", help=_KEY_HELP, placeholder="sk-...", key="llm_api_key")
        st.text_input("Model", placeholder=MODEL, key="llm_model")
        st.text_input("Judge Model", placeholder=MODEL_JUDGE, key="llm_model_judge")
        st.caption("Your key is used only for this request and never saved.")
        st.markdown("---")

    st.caption("Powered by LangGraph + ChromaDB + Opik")


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_query, tab_eval = st.tabs(["Query Interface", "Eval Dashboard"])


# ─── Tab 1: Query Interface ───────────────────────────────────────────────────
with tab_query:
    st.header("Ask a Business Question")
    st.caption("Natural language → SQL → Results. Governance blocks non-SELECT queries automatically.")

    question = st.text_input(
        "Your question",
        placeholder="e.g. How many claims were filed last quarter?",
        key="question_input",
    )

    run_col, _ = st.columns([1, 5])
    run_button = run_col.button("Run Query", type="primary", use_container_width=True)

    if run_button and question.strip():
        _api_key = st.session_state.get("llm_api_key") or None if KEY_FROM_UI else None
        _model   = st.session_state.get("llm_model")   or None if KEY_FROM_UI else None
        if KEY_FROM_UI and not _api_key:
            st.warning("Please enter an API key in the sidebar before running a query.")
            st.stop()
        with st.spinner("Running agent pipeline..."):
            result = run_query_pipeline(question.strip(), api_key=_api_key, model=_model)

        gov = result.get("governance_result", "")
        sql = result.get("generated_sql", "")
        rows = result.get("query_result", [])
        plan = result.get("plan", "")

        # Governance badge
        if gov == "PASSED":
            st.success("Governance: PASSED")
        elif gov.startswith("BLOCKED"):
            st.error(f"Governance: {gov}")
        else:
            st.warning(f"Governance: {gov}")

        # Show agent reasoning in expander
        with st.expander("Agent reasoning (Planner output)", expanded=False):
            st.text(plan)

        # Generated SQL
        st.subheader("Generated SQL")
        st.code(sql, language="sql")

        # Results
        if rows:
            st.subheader(f"Results ({len(rows)} row{'s' if len(rows) != 1 else ''})")
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
        elif gov == "PASSED":
            st.info("Query returned no results.")

        # Feedback
        if gov == "PASSED":
            st.markdown("**Was this answer helpful?**")
            fb_col1, fb_col2, _ = st.columns([1, 1, 6])
            if fb_col1.button("👍 Yes", key="thumbs_up"):
                save_feedback(question, sql, len(rows), thumbs_up=True)
                st.toast("Thanks for the feedback!")
            if fb_col2.button("👎 No", key="thumbs_down"):
                save_feedback(question, sql, len(rows), thumbs_up=False)
                st.toast("Feedback saved. We'll use it to improve.")

    elif run_button:
        st.warning("Please enter a question.")


# ─── Tab 2: Eval Dashboard ────────────────────────────────────────────────────
with tab_eval:
    st.header("Evaluation Dashboard")
    st.caption("Runs the golden dataset through the agent and scores against ship/no-ship thresholds.")

    run_eval_col, quick_col, _ = st.columns([2, 2, 4])

    _n_seeds = len(json.loads(SEED_QUERIES_PATH.read_text())) if SEED_QUERIES_PATH.exists() else 0

    run_full = run_eval_col.button("Run Full Evaluation", type="primary")
    run_quick = quick_col.button(f"Quick Run ({_n_seeds} seeds)")

    max_entries = None
    if run_quick:
        max_entries = _n_seeds

    if run_full or run_quick:
        from evaluation.pipeline import run_evaluation
        golden_path = Path("dataset/golden_dataset.json")
        if not golden_path.exists():
            st.error(
                "Golden dataset not found. Run first:\n"
                "```\npython dataset/generate_dataset.py\n```"
            )
        else:
            progress = st.progress(0, text="Starting evaluation...")
            with st.spinner("Evaluating... this may take a few minutes."):
                output = run_evaluation(max_entries=max_entries)
            progress.progress(100, text="Done!")
            st.success("Evaluation complete! Results saved.")

    # Load and display last results
    if EVAL_RESULTS_PATH.exists():
        output = json.loads(EVAL_RESULTS_PATH.read_text())
        gate = output["gate"]
        results = output["results"]

        st.markdown(f"**Last run:** {output['run_at']} UTC  |  **Entries evaluated:** {output['total_entries']}")

        # Ship / No-Ship badge
        if gate["ship"]:
            st.success("SHIP — All thresholds met")
        else:
            st.error("NO-SHIP — One or more thresholds not met")

        # Metric gauges
        m1, m2, m3 = st.columns(3)
        metrics = [
            ("SQL Validity", "sql_validity", m1),
            ("Execution Accuracy", "execution_accuracy", m2),
            ("Answer Relevance", "answer_relevance", m3),
        ]
        for label, key, col in metrics:
            g = gate[key]
            color = "green" if g["pass"] else "red"
            col.metric(
                label=label,
                value=f"{g['score']:.1%}",
                delta=f"threshold {g['threshold']:.0%}",
                delta_color="normal" if g["pass"] else "inverse",
            )
            col.progress(min(g["score"], 1.0))

        # Per-query results table
        st.subheader("Per-Query Results")
        df = pd.DataFrame(results)

        if df.empty:
            st.info("Evaluation produced no results. Re-run the evaluation.")
            st.stop()

        # Filters
        fcol1, fcol2, fcol3 = st.columns(3)
        complexity_opts = ["All"] + sorted(df["complexity"].dropna().unique().tolist())
        risk_opts = ["All"] + sorted(df["risk_level"].dropna().unique().tolist())
        domain_opts = ["All"] + sorted(df["domain"].dropna().unique().tolist())

        complexity_filter = fcol1.selectbox("Complexity", complexity_opts)
        risk_filter = fcol2.selectbox("Risk Level", risk_opts)
        domain_filter = fcol3.selectbox("Domain", domain_opts)

        filtered = df.copy()
        if complexity_filter != "All":
            filtered = filtered[filtered["complexity"] == complexity_filter]
        if risk_filter != "All":
            filtered = filtered[filtered["risk_level"] == risk_filter]
        if domain_filter != "All":
            filtered = filtered[filtered["domain"] == domain_filter]

        display_cols = [
            "id", "question", "sql_validity", "execution_accuracy",
            "answer_relevance", "complexity", "risk_level", "latency_ms",
        ]
        st.dataframe(
            filtered[display_cols].rename(columns={
                "sql_validity": "valid",
                "execution_accuracy": "accuracy",
                "answer_relevance": "relevance",
                "latency_ms": "ms",
            }),
            use_container_width=True,
        )

        # Drill into a specific result
        with st.expander("Inspect a specific result"):
            entry_ids = filtered["id"].tolist()
            if entry_ids:
                selected_id = st.selectbox("Select entry", entry_ids)
                row = filtered[filtered["id"] == selected_id].iloc[0]
                st.markdown(f"**Question:** {row['question']}")
                st.code(row.get("ground_truth_sql", ""), language="sql")
                st.markdown("**Generated SQL:**")
                st.code(row.get("generated_sql", ""), language="sql")
                st.markdown(f"**Governance:** `{row.get('governance_result', '')}`")
    else:
        st.info("No evaluation results yet. Run an evaluation above.")
