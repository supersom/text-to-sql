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

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPIK_API_KEY = os.getenv("OPIK_API_KEY")
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME", "text-sql-clearspeed")

MODEL = "claude-sonnet-4-6"
MODEL_JUDGE = "claude-haiku-4-5-20251001"

VARIATIONS_PER_SEED = 6

# Ship/no-ship thresholds
THRESHOLD_SQL_VALIDITY = 0.90
THRESHOLD_EXECUTION_ACCURACY = 0.70
THRESHOLD_ANSWER_RELEVANCE = 0.75

FORBIDDEN_SQL_KEYWORDS = {"DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "REPLACE"}
