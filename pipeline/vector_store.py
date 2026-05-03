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

# ── Monkey-patch: ChromaDB client/server version mismatch ─────────────────────
# Newer ChromaDB clients (0.5.7+) expect '_type' in collection metadata JSON,
# but older Chroma Cloud servers do not return it. Patch the deserializer to
# inject a default so that get_or_create_collection / get_collection work.
try:
    from chromadb.api.configuration import CollectionConfigurationInternal
    _orig_from_json = CollectionConfigurationInternal.from_json

    @classmethod
    def _patched_from_json(cls, json_map):
        if isinstance(json_map, dict) and "_type" not in json_map:
            json_map = dict(json_map)
            json_map["_type"] = "CollectionConfigurationInternal"
        return _orig_from_json.__func__(cls, json_map)

    CollectionConfigurationInternal.from_json = _patched_from_json
    logger.info("Applied CollectionConfigurationInternal.from_json monkey-patch for _type fallback")
except Exception:
    pass  # Older chromadb versions don't have this module/class

# ── Configuration ─────────────────────────────────────────────────────────────
COLLECTION_NAME = "sbi_mf_knowledge"
CHROMA_API_KEY = (os.getenv("CHROMA_API_KEY") or "").strip()
CHROMA_TENANT = (os.getenv("CHROMA_TENANT") or "").strip()
CHROMA_DATABASE = (os.getenv("CHROMA_DATABASE") or "default").strip()

# ── Service Class ─────────────────────────────────────────────────────────────

class VectorStore:
    def __init__(self):
        # ── Debug Statements ──────────────────────────────────────────────────
        print(f"DEBUG: CHROMA_TENANT type: {type(os.getenv('CHROMA_TENANT'))}")
        print(f"DEBUG: CHROMA_TENANT length: {len(os.getenv('CHROMA_TENANT', '').strip())}")
        print(f"DEBUG: Environment keys available: {[k for k in os.environ.keys() if 'CHROMA' in k]}")
        # ──────────────────────────────────────────────────────────────────────

        if not CHROMA_API_KEY:
            msg = "CRITICAL ERROR: CHROMA_API_KEY is empty or missing after stripping whitespace."
            logger.error(msg)
            raise ValueError(msg)
        
        if not CHROMA_TENANT:
            msg = "CRITICAL ERROR: CHROMA_TENANT is empty or missing."
            logger.error(msg)
            raise ValueError(msg)
        
        logger.info("Connecting to Chroma Cloud (Tenant: %s, DB: %s)", CHROMA_TENANT, CHROMA_DATABASE)
        
        try:
            # Connect to Chroma Cloud using CloudClient
            self.client = chromadb.CloudClient(
                api_key=CHROMA_API_KEY,
                tenant=CHROMA_TENANT,
                database=CHROMA_DATABASE
            )
            
            # Get or create the collection
            # NOTE: ChromaDB 0.6+ Cloud manages HNSW config server-side.
            # If a collection was created with an older client that stored
            # hnsw:* keys in its metadata, the 0.6.3 client will reject
            # those keys with "Invalid parameter name: hnsw" when fetching
            # the collection.  The recovery path is: delete → recreate.
            try:
                self.collection = self.client.get_or_create_collection(
                    name=COLLECTION_NAME
                )
            except (Exception, KeyError) as init_err:
                err_str = str(init_err)
                if "Invalid parameter" in err_str and "hnsw" in err_str.lower():
                    logger.warning(
                        "Collection '%s' has stale HNSW metadata from an older "
                        "client version. Deleting and recreating...", COLLECTION_NAME
                    )
                    try:
                        self.client.delete_collection(name=COLLECTION_NAME)
                        logger.info("Deleted corrupted collection '%s'", COLLECTION_NAME)
                    except Exception as del_err:
                        logger.warning("Delete attempt: %s (may already be gone)", del_err)
                    self.collection = self.client.create_collection(
                        name=COLLECTION_NAME
                    )
                    logger.info("Recreated collection '%s' with clean config", COLLECTION_NAME)
                elif isinstance(init_err, KeyError):
                    import chromadb as _cd
                    msg = (
                        f"ChromaDB collection config deserialization failed "
                        f"(KeyError: {init_err}). Client version: {_cd.__version__}. "
                        f"This usually means client/server version mismatch."
                    )
                    logger.error(msg)
                    raise RuntimeError(msg) from init_err
                else:
                    raise

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

if __name__ == "__main__":
    # Test connection and collection initialization
    logging.basicConfig(level=logging.INFO)
    try:
        vs = get_vector_store()
        print(f"SUCCESS: Connected to collection '{COLLECTION_NAME}'")
        print(f"Current count: {vs.get_count()}")
    except Exception as e:
        print(f"ERROR: {e}")
