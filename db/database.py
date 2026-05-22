import re
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
    # Use INSERT OR IGNORE so re-runs are safe on an existing DB
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


# ── Per-table schema chunks ──────────────────────────────────────────────────
# Parsed from db/schema.sql at import time — schema.sql is the single source of truth.
# Compact column signatures are auto-generated; inline SQL comments become annotation
# lines; -- @desc comments above each CREATE TABLE become the purpose sentence.

_SCHEMA_SQL = Path(__file__).parent / "schema.sql"


def _parse_schema_chunks(sql_path: Path = _SCHEMA_SQL) -> dict[str, str]:
    lines = sql_path.read_text().splitlines()
    chunks: dict[str, str] = {}

    for i, line in enumerate(lines):
        m = re.match(r'\s*CREATE TABLE IF NOT EXISTS (\w+)\s*\(', line, re.I)
        if not m:
            continue
        table_name = m.group(1)

        # Find the nearest -- @desc comment above this CREATE TABLE
        desc = ''
        j = i - 1
        while j >= 0:
            prev = lines[j].strip()
            if not prev:
                break
            if prev.startswith('--'):
                comment = prev.lstrip('-').strip()
                if comment.startswith('@desc '):
                    desc = comment[6:].strip()
                    break
                j -= 1
            else:
                break

        # Parse column definitions until );
        sig_parts: list[str] = []
        annotations: list[str] = []
        k = i + 1
        while k < len(lines):
            raw = lines[k]
            k += 1
            stripped = raw.strip()
            if stripped.startswith(');') or stripped == ')':
                break
            # Split off inline comment
            inline = ''
            if '--' in raw:
                col_part, _, comment_part = raw.partition('--')
                inline = comment_part.strip()
                stripped = col_part.strip().rstrip(',').strip()
            else:
                stripped = stripped.rstrip(',').strip()
            if not stripped:
                continue
            # Skip table-level constraints
            if re.match(r'(PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE\s*\(|CHECK\s*\()', stripped, re.I):
                continue
            parts = stripped.split()
            if not parts:
                continue
            col_name = parts[0]
            upper = stripped.upper()
            col_type = parts[1].upper() if len(parts) > 1 else ''
            if 'PRIMARY KEY' in upper:
                sig_parts.append(f'{col_name} PK')
            elif ref := re.search(r'REFERENCES\s+(\w+)\s*\(', stripped, re.I):
                sig_parts.append(f'{col_name} FK→{ref.group(1)}')
            elif col_type == 'DATE':
                nullable = 'NOT NULL' not in upper
                sig_parts.append(f'{col_name} DATE{" nullable" if nullable else ""}')
            elif col_type == 'REAL':
                sig_parts.append(f'{col_name} REAL')
            elif ' UNIQUE' in upper:
                sig_parts.append(f'{col_name} UNIQUE')
            else:
                sig_parts.append(col_name)
            if inline:
                annotations.append(f'  {col_name}: {inline}')

        chunk_lines = [f'{table_name}({", ".join(sig_parts)})'] + annotations
        if desc:
            chunk_lines.append(f'  {desc}')
        chunks[table_name] = '\n'.join(chunk_lines)

    return chunks


_TABLE_CHUNKS: dict[str, str] = _parse_schema_chunks()



def get_table_chunks() -> list[dict[str, str]]:
    """Return per-table schema chunks suitable for embedding in the vector store."""
    return [{"name": name, "description": desc} for name, desc in _TABLE_CHUNKS.items()]


def get_all_table_names() -> list[str]:
    return list(_TABLE_CHUNKS.keys())


def get_schema_str() -> str:
    """Full schema description injected into LLM prompts when retrieval is disabled."""
    header = "Database: ClearSpeed Insurance Analytics (SQLite)\n\nTables:"
    body = "\n\n".join(f"  {desc}" for desc in _TABLE_CHUNKS.values())
    footer = (
        "\nRelationships (FK chains):\n"
        "  claims → policies, adjusters\n"
        "  claimants, fraud_flags, claim_documents, claim_assessments,\n"
        "    claim_payments, claim_appeals, repair_estimates,\n"
        "    fraud_investigations, reserve_estimates → claims\n"
        "  policy_coverages, policy_endorsements, premium_payments,\n"
        "    insured_properties, insured_vehicles, risk_assessments,\n"
        "    inspection_reports → policies\n"
        "  risk_assessments → underwriters\n"
        "  repair_estimates → repair_vendors\n"
        "  fraud_investigations → investigators\n"
        "  agent_performance → agents\n"
        "  customer_risk_profiles → customers\n"
        "  policy_coverages → coverage_types\n\n"
        "Date format: YYYY-MM-DD. Use SQLite date functions: date(), strftime(), julianday()."
    )
    return f"{header}\n\n{body}\n{footer}"


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
    print(f"\nTotal tables: {len(get_all_table_names())}")
