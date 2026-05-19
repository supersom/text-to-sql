---
title: Text-to-SQL Insurance Analytics
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.35.0"
app_file: app.py
pinned: false
---

# Text-to-SQL — NLP Query Interface

A local, enterprise-grade Text-to-SQL application that translates natural language questions into executable SQL queries using Claude. Built with a LangGraph multi-agent pipeline, a golden dataset evaluation framework, and OPIK for experiment tracking.

---

## Application Architecture

```
text-sql/
├── .env                        # API keys (never commit this)
├── .env.example                # Key template — copy to .env
├── config.py                   # Central config: model names, thresholds, paths
├── requirements.txt
│
├── db/
│   ├── schema.sql              # SQLite DDL — 30 insurance/claims tables
│   ├── seed_data.sql           # Sample insurance data across all 30 tables
│   ├── database.py             # init_db(), run_query(), get_schema_str(), get_table_chunks()
│   └── schema_store.py         # build_schema_store(), retrieve_schema() — ChromaDB vector store
│
├── dataset/
│   ├── seed_queries.json       # 20 SME-curated ground-truth Q+SQL pairs
│   ├── generate_dataset.py     # Phase 1: expands seeds to 120+ variations via Claude
│   ├── golden_dataset.json     # Generated output (created by generate_dataset.py)
│   └── derive_needed_tables.py # Parses golden_dataset.json to populate needed_tables per entry
│
├── agents/
│   ├── graph.py                # LangGraph StateGraph — wires the 3 agents together
│   ├── planner.py              # Agent 1: retrieves relevant schema, decomposes question into a query plan
│   ├── sql_generator.py        # Agent 2: converts plan to a SELECT-only SQL query
│   └── governance.py           # Agent 3: blocks unsafe SQL, executes the query
│
├── evaluation/
│   ├── metrics.py              # 4 scoring functions (validity, accuracy, relevance, schema_recall)
│   ├── pipeline.py             # Runs golden dataset through agents via opik.evaluate(), logs to OPIK
│   └── manual_pipeline.py      # Alternative: sequential per-entry evaluation with @track decorators
│
└── app.py                      # Streamlit UI — Query tab + Eval Dashboard tab
```

### Agent Pipeline (LangGraph)

```
User Question
     │
     ▼
┌─────────────┐     ┌───────────────────┐     ┌──────────────────┐
│   Planner   │────▶│  SQL Generator    │────▶│   Governance     │
│  (Claude)   │     │  (Claude)         │     │  (Heuristic)     │
│             │     │                   │     │                  │
│ Decomposes  │     │ Generates a       │     │ Blocks non-SELECT│
│ question →  │     │ SELECT-only       │     │ and forbidden    │
│ query plan  │     │ SQLite query      │     │ keywords, then   │
│             │     │                   │     │ executes the SQL │
└─────────────┘     └───────────────────┘     └──────────────────┘
                                                       │
                                                       ▼
                                                 Result rows
```

### Database Schema (SQLite — 30 tables)

Tables are grouped by domain. See `db/schema.sql` for full DDL.

| Domain | Tables |
|---|---|
| Core | `adjusters`, `policies`, `claims`, `claimants`, `fraud_flags` |
| Parties | `customers`, `agents`, `underwriters` |
| Coverage | `coverage_types`, `loss_types`, `policy_coverages`, `policy_endorsements` |
| Financial | `premium_payments`, `claim_payments`, `reserve_estimates` |
| Assets | `insured_properties`, `insured_vehicles` |
| Risk & Inspection | `risk_assessments`, `inspection_reports` |
| Claims Workflow | `claim_documents`, `claim_assessments`, `claim_appeals` |
| Vendors | `repair_vendors`, `repair_estimates` |
| Fraud | `investigators`, `fraud_investigations` |
| Compliance | `regulatory_filings`, `compliance_audits` |
| Performance | `agent_performance`, `customer_risk_profiles` |

### Evaluation Metrics & Launch Gates

| Metric | Method | Ship Threshold |
|---|---|---|
| SQL Validity | Heuristic — SQL executes without error | > 90% |
| Execution Accuracy | Row-level F1 against ground truth; LLM-as-judge fallback below threshold | > 70% |
| Answer Relevance | LLM-as-Judge — Claude scores semantic alignment of SQL + result to question | > 75% |
| Schema Recall | Heuristic — fraction of required tables covered by the vector store retrieval | > 90% |

---

## How the Application Was Built

### Phase 1 — Foundation & Database
- Designed a 30-table SQLite schema covering the Insurance/Claims domain across 11 functional areas (core, parties, coverage, financial, assets, risk, claims workflow, vendors, fraud, compliance, performance)
- Seeded realistic sample data across all 30 tables with all PII fields redacted
- Built `database.py` with `init_db()`, `run_query()`, `get_schema_str()`, and `get_table_chunks()` — schema context is either retrieved selectively or injected in full depending on `USE_SCHEMA_RETRIEVAL` in `config.py`
- Built `schema_store.py` using ChromaDB to embed all 30 table descriptions as a local vector store; `retrieve_schema(query, k)` returns the `k` most relevant tables for a given question

### Phase 2 — Golden Dataset (Phase 1 of the requirements)
- Authored 20 seed queries with ground-truth SQL covering key business questions: fraud savings, risk distribution, adjuster performance, claim resolution time, vendor estimates, reserve tracking, compliance, and agent commission
- Each entry is tagged: `complexity` (Simple/Medium/Complex), `operations` (Filter/Join/GroupBy/Subquery), `risk_level`, `domain`, and `needed_tables` (required for `schema_recall` scoring)
- `generate_dataset.py` uses Claude to expand each seed into 6 variations — paraphrases, temporal modifiers, typos — producing ~140 entries in `golden_dataset.json`
- `derive_needed_tables.py` parses each ground-truth SQL with sqlglot to populate `needed_tables`; re-run whenever the dataset is regenerated

### Phase 3 — LangGraph Multi-Agent Pipeline
- Built a three-node `StateGraph`: **Planner → SQL Generator → Governance**
- **Planner**: queries the ChromaDB vector store to retrieve the `k` most relevant table descriptions for the question (or injects the full schema when `USE_SCHEMA_RETRIEVAL=False`), then uses Claude to produce a structured plan (tables, joins, filters, aggregations); retrieved schema and table names are stored in `AgentState` to avoid a second vector lookup
- **SQL Generator**: reads the schema from `AgentState` and uses Claude to generate a SELECT-only SQLite query; forbidden keywords are enforced at the prompt level
- **Governance**: heuristic layer that blocks any non-SELECT statement and forbidden keywords (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE, REPLACE), then executes the approved query

### Phase 4 — Evaluation Pipeline (Phase 2 of the requirements)
- `metrics.py` implements four scoring functions: `SqlValidityMetric`, `ExecutionAccuracyMetric` (row-level F1 + LLM judge fallback), `AnswerRelevanceMetric` (LLM-as-judge), and `SchemaRecallMetric` (retrieval coverage)
- `pipeline.py` runs the full golden dataset through the agent via `opik.evaluate()`, scores each entry in parallel, logs every trace to OPIK, and prints a ship/no-ship scorecard against configurable thresholds
- `manual_pipeline.py` provides an alternative sequential runner using `@track` decorators for step-by-step OPIK tracing
- Results are saved to `evaluation/results.json` for the UI dashboard

### Phase 5 — Streamlit UI
- **Query tab**: text input → agent pipeline → syntax-highlighted SQL + result table + governance badge. Thumbs up/down feedback is written to `dataset/feedback.json` for future dataset expansion
- **Eval Dashboard tab**: run evaluation in-browser, view metric gauges, ship/no-ship badge, filterable per-query results table, and a drill-down inspector per entry

---

## Running Locally

### Prerequisites
- Python 3.11+
- An Anthropic API key
- An OPIK (Comet) API key

### 1. Clone and enter the project

```bash
cd text-sql
```

### 2. Create and activate the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```
LLM_API_KEY=sk-ant-...        # API key for whichever provider MODEL points to
OPIK_API_KEY=...
OPIK_PROJECT_NAME=text_to_sql_pm_demo
```

### 5. Initialize the database

```bash
python db/database.py
```

Expected output:
```
Database ready. Total claims: <n>
Claims by risk level:
  High: <n> claims, $<amount>
  ...
Total tables: 30
```

### 5a. Build the schema vector store

Embeds all 30 table descriptions into a local ChromaDB store (runs once, ~10 seconds on first run while the embedding model downloads):

```bash
python db/schema_store.py
```

Expected output:
```
Schema store built: 30 tables indexed at data/schema_store
```

The store is used by the agent pipeline to retrieve the top-k most relevant tables per query instead of injecting all 30. The value of `k` is set by `SCHEMA_RETRIEVAL_TOP_K` in `config.py`. Set `USE_SCHEMA_RETRIEVAL = False` to compare against full-schema injection — schema_recall will be trivially 1.0 in that mode.

### 6. Generate the golden dataset (Phase 1 — runs once)

This calls Claude ~120 times to expand 20 seed queries into ~140 variations. Takes ~3 minutes and costs a small amount in API credits.

```bash
python dataset/generate_dataset.py
```

Output: `dataset/golden_dataset.json`

Then derive `needed_tables` for each entry (required for the `schema_recall` metric):

```bash
python dataset/derive_needed_tables.py
```

Use `--dry-run` to preview extracted tables without modifying the file. Re-run this whenever `golden_dataset.json` is regenerated.

### 7. Launch the Streamlit app

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

- **Query tab**: type any insurance/claims question in plain English
- **Eval Dashboard tab**: click "Quick Run (12 seeds)" for a fast smoke test, or "Run Full Evaluation" for the complete golden dataset

### 8. (Optional) Run evaluation from the CLI

```bash
# Quick run — 12 seeds only
python evaluation/pipeline.py --max 12

# Full run
python evaluation/pipeline.py
```

---

## Security Notes

- `.env` is excluded from version control — never commit it
- The Governance agent blocks all non-SELECT SQL (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE, REPLACE) at the heuristic layer before any execution
- Sample data has all PII fields redacted (`full_name`, `contact_email` contain only `"Redacted"`)
