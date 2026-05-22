# Eval Pipeline Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                     ONE-TIME SETUP (run once)                   │
└─────────────────────────────────────────────────────────────────┘

  db/schema.sql ──┐
  db/seed_data.sql┘──▶  [init_db()]  ──▶  data/insurance.db
        │
        │  [_parse_schema_chunks()]         (at import time)
        ▼
  -- @desc comments    ──▶  [build_schema_store()]  ──▶  data/schema_store/
  + inline col comments      ChromaDB embeddings            (ChromaDB)
  (db/schema.sql is the
   single source of truth)


┌─────────────────────────────────────────────────────────────────┐
│                  PHASE 1: DATASET GENERATION                    │
│             python dataset/generate_dataset.py                  │
└─────────────────────────────────────────────────────────────────┘

  dataset/seed_queries.json
  (hand-written Q + SQL)
          │
          ▼
  [LLM: generate variations]  ◀── MODEL (claude-sonnet-4-6)
  6 variants per seed:               ◀── VARIATIONS_PER_SEED=6
    • paraphrase / business-speak
    • temporal modifiers
    • entity value changes
    • typos / ambiguity
          │
          ▼
  dataset/golden_dataset.json
  (seeds + variants; ~72-120 entries)
          │
          ▼
  [derive_needed_tables.py]
  parse ground_truth_sql with sqlglot
  → extract table names → write needed_tables field in-place
          │
          ▼
  dataset/golden_dataset.json  ✓ (final, with needed_tables)


┌─────────────────────────────────────────────────────────────────┐
│                   PHASE 2: QUERY PIPELINE                       │
│          (runs once per question, inside the eval loop)         │
└─────────────────────────────────────────────────────────────────┘

  question
     │
     ▼
  [Schema Retrieval]  ◀── data/schema_store/ (ChromaDB)
  vector similarity search        ◀── SCHEMA_RETRIEVAL_TOP_K=5
  → top-k table descriptions              (or full schema if disabled)
     │
     ▼
  [Planner Agent]  ◀── LLM (MODEL)
  question + schema → structured plan
  (TABLES / JOINS / FILTERS / AGGREGATIONS / INTENT)
  → state: plan, retrieved_schema, retrieved_tables
     │
     ▼
  [SQL Generator Agent]  ◀── LLM (MODEL)
  question + plan + schema → raw SQLite SELECT
  → state: generated_sql
     │
     ▼
  [Governance]
  ├── reject if not SELECT
  ├── reject if FORBIDDEN keyword (DROP/DELETE/UPDATE/…)
  ├── execute against data/insurance.db
  └── → state: governance_result, query_result, answer


┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3: EVALUATION                          │
│              python evaluation/pipeline.py                      │
│             (or via Run Evaluation button in UI)                │
└─────────────────────────────────────────────────────────────────┘

  dataset/golden_dataset.json
          │
          │  for each entry:
          │    run_query_pipeline(question)  [Phase 2 above]
          │          │
          ▼          ▼
  ┌──────────────────────────────────────────┐
  │              4 METRICS                   │
  │                                          │
  │  SQL Validity (heuristic)                │
  │    executes without error? → 0 or 1      │
  │                                          │
  │  Execution Accuracy (F1 + LLM fallback)  │
  │    row-level F1 vs ground-truth rows     │
  │    if F1 < threshold → LLM judge         │  ◀── MODEL_JUDGE
  │                                          │
  │  Answer Relevance (LLM judge)            │
  │    does SQL answer the question? 0–1     │  ◀── MODEL_JUDGE
  │                                          │
  │  Schema Recall (heuristic)               │
  │    needed_tables ∩ retrieved / needed    │
  └──────────────────────────────────────────┘
          │
          ▼
  [Gate Check]
    sql_validity        ≥ 0.90 ?
    execution_accuracy  ≥ 0.70 ?
    answer_relevance    ≥ 0.75 ?
    schema_recall       ≥ 0.90 ?
          │
          ├── all pass ──▶  ✅ SHIP
          └── any fail ──▶  ❌ NO-SHIP
          │
          ▼
  evaluation/results.json
  (per-entry scores + gate scorecard)
  + OPIK experiment (if configured)


┌─────────────────────────────────────────────────────────────────┐
│                    KEY CONFIG KNOBS                             │
└─────────────────────────────────────────────────────────────────┘

  MODEL               = claude-sonnet-4-6   (planner, SQL gen, expansion)
  MODEL_JUDGE         = claude-haiku-4-5    (accuracy + relevance judge)
  LLM_BACKEND         = api | claude-cli | gemini-cli | codex-cli
  USE_SCHEMA_RETRIEVAL= True                (False → always inject full schema)
  SCHEMA_RETRIEVAL_TOP_K = 5
  VARIATIONS_PER_SEED = 6
  TASK_THREADS        = 2                   (parallel eval workers)
  THRESHOLDS          = 0.90 / 0.70 / 0.75 / 0.90
```
