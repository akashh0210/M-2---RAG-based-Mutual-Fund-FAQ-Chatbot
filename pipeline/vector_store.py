"""
pipeline/vector_store.py
Phase 3 — Chroma Cloud Vector Store Service

Handles initialization and connection to the managed Chroma Cloud store.
Collection: sbi_mf_knowledge
Dimensions: 768 (BGE-Base-en-v1.5)
"""

import os
import logging
from typing import List, Dict, Any, Optional

import chromadb
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("pipeline.vector_store")

# ── Configuration ─────────────────────────────────────────────────────────────
COLLECTION_NAME = "sbi_mf_knowledge"
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "default")

# ── Service Class ─────────────────────────────────────────────────────────────

class VectorStore:
    def __init__(self):
        if not CHROMA_API_KEY:
            logger.error("CHROMA_API_KEY not found in environment. Vector store will fail.")
        
        logger.info("Connecting to Chroma Cloud (Tenant: %s, DB: %s)", CHROMA_TENANT, CHROMA_DATABASE)
        
        try:
            # Connect to Chroma Cloud using CloudClient
            self.client = chromadb.CloudClient(
                api_key=CHROMA_API_KEY,
                tenant=CHROMA_TENANT,
                database=CHROMA_DATABASE
            )
            
            # Get or create the collection
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Successfully connected to Chroma Cloud collection: %s", COLLECTION_NAME)
        except Exception as e:
            logger.error("Failed to connect to Chroma Cloud: %s", e)
            raise

    def upsert_chunks(
        self, 
        ids: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]], 
        documents: List[str]
    ) -> None:
        """Upsert a batch of chunks into Chroma Cloud."""
        try:
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            logger.info("Successfully upserted %d chunks to Chroma Cloud", len(ids))
        except Exception as e:
            logger.error("Failed to upsert chunks to Chroma Cloud: %s", e)
            raise

    def query(self, query_embeddings: List[List[float]], n_results: int = 5, where: Optional[Dict] = None):
        """Query the cloud collection for nearest neighbors."""
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )

    def get_count(self) -> int:
        """Return total number of items in the cloud collection."""
        return self.collection.count()

# Singleton instance
_vs_instance = None

def get_vector_store() -> VectorStore:
    global _vs_instance
    if _vs_instance is None:
        _vs_instance = VectorStore()
    return _vs_instance
