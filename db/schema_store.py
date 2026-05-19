"""
Schema vector store (ChromaDB).

Each of the 30 tables is stored as one document. At query time, the top-k
most semantically similar tables are retrieved and injected into the prompt
instead of the full 30-table schema.

Build / rebuild:
    python db/schema_store.py

Use in agents:
    from db.schema_store import retrieve_schema
    schema_str, table_names = retrieve_schema("your question here")
"""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from config import VECTOR_DB_PATH, SCHEMA_RETRIEVAL_TOP_K
from db.database import get_table_chunks, get_schema_str, get_all_table_names

COLLECTION_NAME = "table_schemas"


def _client() -> chromadb.PersistentClient:
    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(VECTOR_DB_PATH))


def build_schema_store() -> None:
    """Embed all table chunks and persist to the vector store. Safe to re-run."""
    client = _client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    chunks = get_table_chunks()
    collection.add(
        documents=[c["description"] for c in chunks],
        ids=[c["name"] for c in chunks],
        metadatas=[{"table_name": c["name"]} for c in chunks],
    )
    print(f"Schema store built: {len(chunks)} tables indexed at {VECTOR_DB_PATH}")


def retrieve_schema(
    query: str,
    k: int = SCHEMA_RETRIEVAL_TOP_K,
) -> tuple[str, list[str]]:
    """
    Return the top-k most relevant table descriptions for the query.

    Returns (schema_string, table_names). Falls back to the full schema and
    all table names if the store has not been built yet.
    """
    try:
        client = _client()
        collection = client.get_collection(COLLECTION_NAME)
        results = collection.query(query_texts=[query], n_results=k)
        docs: list[str] = results["documents"][0]
        names: list[str] = results["ids"][0]
        schema_str = (
            "Database: ClearSpeed Insurance Analytics (SQLite)\n\n"
            "Relevant tables:\n\n"
            + "\n\n".join(f"  {d}" for d in docs)
            + "\n\nDate format: YYYY-MM-DD. "
            "Use SQLite date functions: date(), strftime(), julianday()."
        )
        return schema_str, names
    except Exception:
        warnings.warn(
            "Schema vector store not found — falling back to full schema. "
            "Run: python db/schema_store.py",
            UserWarning,
            stacklevel=2,
        )
        return get_schema_str(), get_all_table_names()


if __name__ == "__main__":
    build_schema_store()
