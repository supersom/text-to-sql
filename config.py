import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")
DB_PATH = BASE_DIR / "data" / "clearspeed.db"
GOLDEN_DATASET_PATH = BASE_DIR / "dataset" / "golden_dataset.json"
SEED_QUERIES_PATH = BASE_DIR / "dataset" / "seed_queries.json"
FEEDBACK_PATH = BASE_DIR / "dataset" / "feedback.json"
EVAL_RESULTS_PATH = BASE_DIR / "evaluation" / "results.json"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # kept for backward compat during migration
LLM_API_KEY = os.getenv("LLM_API_KEY")

OPIK_API_KEY = os.getenv("OPIK_API_KEY")
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME", "text-to-sql-analytics")

MODEL = os.getenv("MODEL", "claude-sonnet-4-6")
MODEL_JUDGE = os.getenv("MODEL_JUDGE", "claude-haiku-4-5-20251001")

VARIATIONS_PER_SEED = 6
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", 4))
LLM_MIN_INTERVAL = float(os.getenv("LLM_MIN_INTERVAL", 0.0))  # min seconds between calls; set >0 for rate-limited providers

# Schema vector store
VECTOR_DB_PATH = BASE_DIR / "data" / "schema_store"
SCHEMA_RETRIEVAL_TOP_K = 5   # tables retrieved per query (out of 30); lower = more selective
USE_SCHEMA_RETRIEVAL = True  # False → inject full schema (schema_recall trivially ~1.0)

# Ship/no-ship thresholds
THRESHOLD_SQL_VALIDITY = 0.90
THRESHOLD_EXECUTION_ACCURACY = 0.70
THRESHOLD_ANSWER_RELEVANCE = 0.75
THRESHOLD_SCHEMA_RECALL = 0.90

FORBIDDEN_SQL_KEYWORDS = {"DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "REPLACE"}
