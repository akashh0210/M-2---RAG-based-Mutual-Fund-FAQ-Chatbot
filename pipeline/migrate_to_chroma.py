"""
pipeline/migrate_to_chroma.py
Phase 3 — ChromaDB Migration Script

Transfers existing BGE embeddings from SQLite to the new ChromaDB vector store.
Standardizes the knowledge base during the architectural transition.
"""

import logging
import json
from pipeline.models import get_connection
from pipeline.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pipeline.migration")

def run_migration():
    logger.info("=" * 70)
    logger.info("ChromaDB Migration Started")
    logger.info("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()
    vs = get_vector_store()

    # Fetch all chunks that have an embedding
    cursor.execute("""
        SELECT 
            c.chunk_id, 
            c.chunk_text, 
            c.source_id,
            c.embedding,
            s.scheme_name,
            s.official_url,
            s.document_type
        FROM source_chunks c
        JOIN source_documents s ON c.source_id = s.source_id
        WHERE c.embedding IS NOT NULL
    """)
    rows = cursor.fetchall()

    if not rows:
        logger.info("No existing embeddings found in SQLite for migration.")
        return

    logger.info("Found %d chunks with embeddings in SQLite. Migrating to ChromaDB...", len(rows))

    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for row in rows:
        try:
            vector = json.loads(row["embedding"])
            ids.append(row["chunk_id"])
            embeddings.append(vector)
            documents.append(row["chunk_text"])
            metadatas.append({
                "source_id": str(row["source_id"]),
                "scheme_name": row["scheme_name"] or "None",
                "official_url": row["official_url"],
                "document_type": row["document_type"]
            })
        except Exception as e:
            logger.error("Failed to parse vector for chunk %s: %s", row["chunk_id"], e)

    # Batch upsert to ChromaDB
    if ids:
        vs.upsert_chunks(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        logger.info("Migration complete. Total chunks in ChromaDB: %d", vs.get_count())
    
    conn.close()

if __name__ == "__main__":
    run_migration()
