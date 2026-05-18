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
│   ├── schema.sql              # SQLite DDL — 5 insurance/claims tables
│   ├── seed_data.sql           # ~200 rows of sample insurance data
│   └── database.py             # init_db(), run_query(), get_schema_str()
│
├── dataset/
│   ├── seed_queries.json       # 12 SME-curated ground-truth Q+SQL pairs
│   ├── generate_dataset.py     # Phase 1: expands seeds to 80+ variations via Claude
│   └── golden_dataset.json     # Generated output (created by generate_dataset.py)
│
├── agents/
│   ├── graph.py                # LangGraph StateGraph — wires the 3 agents together
│   ├── planner.py              # Agent 1: decomposes question into a query plan
│   ├── sql_generator.py        # Agent 2: converts plan to a SELECT-only SQL query
│   └── governance.py           # Agent 3: blocks unsafe SQL, executes the query
│
├── evaluation/
│   ├── metrics.py              # 3 scoring functions (validity, accuracy, relevance)
│   └── pipeline.py             # Runs golden dataset through agents, logs to OPIK
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

### Database Schema (SQLite)

```
adjusters ──────────────────────────────────────────┐
  adjuster_id, name, region, department              │
                                                     │
policies ───────────────────────────────┐            │
  policy_id, domain, policy_type,       │            │
  effective_date, expiry_date,          │            │
  premium, status                       │            │
                                        ▼            ▼
                                      claims ────────┘
                                        claim_id, policy_id, adjuster_id,
                                        filed_date, resolved_date,
                                        amount, status, risk_level
                                          │                │
                              ┌───────────┘                └──────────────┐
                              ▼                                           ▼
                          claimants                                fraud_flags
                            claimant_id, full_name,                 flag_id, flag_type,
                            contact_email, state                    flagged_at, resolved,
                                                                    savings
```

### Evaluation Metrics & Launch Gates

| Metric | Method | Ship Threshold |
|---|---|---|
| SQL Validity | Heuristic — SQL executes without error | > 90% |
| Execution Accuracy | Heuristic — result set matches ground truth exactly | > 70% |
| Answer Relevance | LLM-as-Judge — Claude scores semantic alignment | > 0.75 |

---

## How the Application Was Built

### Phase 1 — Foundation & Database
- Designed a 5-table SQLite schema covering the Insurance/Claims domain: `adjusters`, `policies`, `claims`, `claimants`, `fraud_flags`
- Seeded 25 claims, 20 policies, 10 fraud flags, and 25 claimants with realistic data
- Built `database.py` with `init_db()`, `run_query()`, and `get_schema_str()` — the schema string is injected into every LLM prompt as context

### Phase 2 — Golden Dataset (Phase 1 of the requirements)
- Authored 12 seed queries with ground-truth SQL covering key business questions: fraud savings, risk distribution, adjuster performance, claim resolution time
- Each entry is tagged: `complexity` (Simple/Medium/Complex), `operations` (Filter/Join/GroupBy/Subquery), `risk_level`, `domain`
- `generate_dataset.py` uses Claude to expand each seed into 6 variations — paraphrases, temporal modifiers, typos — producing 80+ entries in `golden_dataset.json`

### Phase 3 — LangGraph Multi-Agent Pipeline
- Built a three-node `StateGraph`: **Planner → SQL Generator → Governance**
- **Planner**: Claude reads the question + schema and produces a structured plan (tables, joins, filters, aggregations)
- **SQL Generator**: Claude reads the plan and generates a SELECT-only SQLite query; forbidden keywords are enforced at the prompt level
- **Governance**: Heuristic layer that blocks any non-SELECT statement and forbidden keywords (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE), then executes the approved query

### Phase 4 — Evaluation Pipeline (Phase 2 of the requirements)
- `metrics.py` implements the three mandatory scoring functions
- `pipeline.py` runs the full golden dataset through the agent, scores each entry, logs every trace to OPIK, and prints a ship/no-ship scorecard
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
ANTHROPIC_API_KEY=sk-ant-...
OPIK_API_KEY=...
OPIK_PROJECT_NAME=text_to_sql_pm_demo
```

### 5. Initialize the database

```bash
python db/database.py
```

Expected output:
```
Database ready. Total claims: 25
Claims by risk level:
  High: 7 claims, $445,000.00
  ...
```

### 6. Generate the golden dataset (Phase 1 — runs once)

This calls Claude ~72 times to expand 12 seed queries into 80+ variations. Takes ~2 minutes and costs a small amount in API credits.

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
- The Governance agent blocks all non-SELECT SQL (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE) at the heuristic layer before any execution
- Sample data has all PII fields redacted (`full_name`, `contact_email` contain only `"Redacted"`)
