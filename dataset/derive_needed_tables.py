"""
Parses ground_truth_sql in golden_dataset.json and writes needed_tables
back into each entry in-place.

Usage:
    python dataset/derive_needed_tables.py
    python dataset/derive_needed_tables.py --dry-run   # print without writing
"""
import argparse
import json
import sys
from pathlib import Path

import sqlglot
import sqlglot.expressions as exp

DATASET_PATH = Path(__file__).parent / "golden_dataset.json"


def extract_needed_tables(sql: str) -> list[str]:
    """Return sorted list of table names referenced in sql."""
    try:
        parsed = sqlglot.parse_one(sql, dialect="sqlite")
    except sqlglot.errors.ParseError as e:
        raise ValueError(f"Failed to parse SQL: {e}") from e

    tables = {table.name.lower() for table in parsed.find_all(exp.Table) if table.name}
    return sorted(tables)


def main(dry_run: bool = False) -> None:
    dataset = json.loads(DATASET_PATH.read_text())

    errors = []
    for entry in dataset:
        eid = entry["id"]
        sql = entry.get("ground_truth_sql", "")
        try:
            entry["needed_tables"] = extract_needed_tables(sql)
        except ValueError as e:
            errors.append(eid)
            print(f"  WARN [{eid}]: {e}", file=sys.stderr)
            entry["needed_tables"] = []

        print(f"  {eid}: {entry['needed_tables']}")

    if dry_run:
        print("\n--dry-run: no file written.")
        return

    DATASET_PATH.write_text(json.dumps(dataset, indent=2))
    print(f"\nWrote needed_tables to {DATASET_PATH}  ({len(dataset)} entries, {len(errors)} errors)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print results without modifying the file")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
