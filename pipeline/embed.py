"""
pipeline/embed.py
Phase 3 — Embedding Service (Updated for BGE-Base-en-v1.5)

Generates vector embeddings for all pending chunks in the database.
Primary model: BAAI/bge-base-en-v1.5 (768 dimensions)
Runs locally via sentence-transformers.

Vectors are stored as JSON-serialized strings in the SQLite 'embedding' column.
"""

import json
import logging
import os
from typing import List, Optional

from tqdm import tqdm
from pipeline.models import get_connection, update_chunk_embedding
from pipeline.vector_store import get_vector_store

logger = logging.getLogger("pipeline.embed")

# ── Configuration ─────────────────────────────────────────────────────────────
BATCH_SIZE = 32
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"

# ── Main Entry Point ──────────────────────────────────────────────────────────

def run_embedding() -> None:
    """Batch embed all chunks with embedding_status='pending'."""
    logger.info("=" * 70)
    logger.info("Embedding run started (Model: %s)", EMBEDDING_MODEL_NAME)
    logger.info("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()
    vs = get_vector_store()

    # Get pending chunks with metadata needed for ChromaDB
    cursor.execute("""
        SELECT 
            c.chunk_id, 
            c.chunk_text, 
            c.source_id,
            s.scheme_name,
            s.official_url,
            s.document_type
        FROM source_chunks c
        JOIN source_documents s ON c.source_id = s.source_id
        WHERE c.embedding_status = 'pending'
    """)
    rows = cursor.fetchall()
    
    if not rows:
        logger.info("No pending chunks found for embedding")
        conn.close()
        return

    logger.info("Found %d pending chunks", len(rows))

    # Initialize model
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading model: %s...", EMBEDDING_MODEL_NAME)
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    except ImportError:
        logger.error("sentence-transformers package not found. Run: pip install sentence-transformers")
        raise
    except Exception as e:
        logger.error("Failed to load model %s: %s", EMBEDDING_MODEL_NAME, e)
        raise

    # Process in batches
    for i in tqdm(range(0, len(rows), BATCH_SIZE), desc="Embedding Batches"):
        batch = rows[i : i + BATCH_SIZE]
        chunk_ids = [row["chunk_id"] for row in batch]
        texts = [row["chunk_text"] for row in batch]

        try:
            # BGE-base-en-v1.5 from sentence-transformers
            embeddings = model.encode(texts, normalize_embeddings=True)
            vectors = [vec.tolist() for vec in embeddings]

            # Prepare metadata for ChromaDB
            metadatas = []
            for row in batch:
                metadatas.append({
                    "source_id": str(row["source_id"]),
                    "scheme_name": row["scheme_name"] or "None",
                    "official_url": row["official_url"],
                    "document_type": row["document_type"]
                })

            # Upsert into ChromaDB
            vs.upsert_chunks(
                ids=chunk_ids,
                embeddings=vectors,
                metadatas=metadatas,
                documents=texts
            )

            # Update SQLite status
            for cid, vector in zip(chunk_ids, vectors):
                update_chunk_embedding(conn, cid, vector)

        except Exception as e:
            logger.error("Batch failed at index %d: %s", i, e)

    conn.close()
    logger.info("Embedding run complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_embedding()
