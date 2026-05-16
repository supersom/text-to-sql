import sqlite3
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    base = Path(__file__).parent
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript((base / "schema.sql").read_text())
    # Only seed if tables are empty
    row = cursor.execute("SELECT COUNT(*) FROM adjusters").fetchone()
    if row[0] == 0:
        cursor.executescript((base / "seed_data.sql").read_text())
    conn.commit()
    conn.close()


def run_query(sql: str) -> tuple[list[dict], str | None]:
    """Execute a SQL query. Returns (rows, error). rows is [] on error."""
    try:
        conn = get_connection()
        cursor = conn.execute(sql)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows, None
    except Exception as e:
        return [], str(e)


def get_schema_str() -> str:
    """Return a concise schema description for LLM context."""
    return """
Database: ClearSpeed Insurance Analytics (SQLite)

Tables:
  adjusters(adjuster_id PK, name, region, department)
    region: 'Northeast'|'Southeast'|'Midwest'|'West'
    department: 'Auto'|'Property'|'Health'|'Liability'

  policies(policy_id PK, holder_name, domain, policy_type, effective_date DATE, expiry_date DATE, premium REAL, status)
    domain: 'Insurance'|'Banking'|'Public Sector'
    policy_type: 'Auto'|'Property'|'Health'|'Liability'
    status: 'Active'|'Expired'|'Cancelled'|'Pending'

  claims(claim_id PK, policy_id FK→policies, adjuster_id FK→adjusters, filed_date DATE, resolved_date DATE nullable, amount REAL, status, risk_level)
    status: 'Open'|'Approved'|'Denied'|'Under Review'
    risk_level: 'Low'|'Medium'|'High'

  claimants(claimant_id PK, claim_id FK→claims, full_name, contact_email, state)
    state: 2-letter US state code

  fraud_flags(flag_id PK, claim_id FK→claims, flag_type, flagged_at DATE, resolved INTEGER 0/1, savings REAL)
    flag_type: 'Duplicate'|'Inflated Amount'|'Staged Incident'|'Identity Mismatch'
    resolved: 0=open, 1=resolved
    savings: estimated fraud savings in USD

Relationships:
  claims → policies (many claims per policy)
  claims → adjusters (many claims per adjuster)
  claimants → claims (one claimant per claim)
  fraud_flags → claims (many flags per claim)

Date format: YYYY-MM-DD. Use SQLite date functions (date(), strftime()) for date math.
""".strip()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    rows, err = run_query("SELECT COUNT(*) as total_claims FROM claims")
    if err:
        print(f"Error: {err}")
    else:
        print(f"Database ready. Total claims: {rows[0]['total_claims']}")
    rows, _ = run_query(
        "SELECT risk_level, COUNT(*) as cnt, SUM(amount) as total "
        "FROM claims GROUP BY risk_level ORDER BY risk_level"
    )
    print("\nClaims by risk level:")
    for r in rows:
        print(f"  {r['risk_level']}: {r['cnt']} claims, ${r['total']:,.2f}")
