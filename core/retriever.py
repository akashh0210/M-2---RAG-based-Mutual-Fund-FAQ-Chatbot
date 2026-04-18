"""
core/retriever.py
Phase 4 — Hybrid Retrieval Service

Combines Structured Fact Card lookup (exact) with Vector Search (semantic).
Connects to SQLite for facts and Chroma Cloud for vectors.
"""

import logging
import sqlite3
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from pipeline.vector_store import get_vector_store
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("core.retriever")

# ── Evidence Schema ───────────────────────────────────────────────────────────

class RetrievalResult(BaseModel):
    source: str  # 'fact_card' | 'vector_search'
    content: str
    metadata: Dict[str, Any]
    score: float = 1.0

# ── Service Class ─────────────────────────────────────────────────────────────

class Retriever:
    def __init__(self, db_path: str = "data/rag.db", model_name: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.vs = get_vector_store()
        logger.info("Loading embedding model for retrieval: %s", model_name)
        self.model = SentenceTransformer(model_name)

    def _get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def retrieve(self, query: str, intent: str, scheme_name: Optional[str] = None, fact_type: Optional[str] = None) -> List[RetrievalResult]:
        """Execute hybrid retrieval with deterministic citation selection."""
        
        results = []

        # 1. Structured Fact Card Lookup
        if intent == "scheme_fact" and scheme_name:
            fact_result = self._lookup_fact_card(scheme_name, fact_type)
            if fact_result:
                results.append(fact_result)

        # 2. Vector Search (Chroma Cloud)
        vector_results = self._search_vectors(query, scheme_name)
        results.extend(vector_results)

        # 3. Deterministic Citation Sorting (Phase 5)
        # We sort by priority score first (lower is better), then by distance score (if applicable)
        results.sort(key=lambda x: (self._get_priority_score(x.metadata.get("source_url", "") or x.metadata.get("official_url", "")), -x.score))

        return results

    def _get_priority_score(self, url: str) -> int:
        """
        Assign a priority score to a URL. Lower is higher priority.
        1: Factsheets/KIM/SID
        2: Scheme Detail Pages
        3: Service Portals
        4: Educational/Regulatory (AMFI/SEBI)
        5: Everything else
        """
        if not url:
            return 5
            
        u = url.lower()
        if any(x in u for x in ["factsheet", "sid-kim", "offer-document", "document-sid"]):
            return 1
        if "sbimf-scheme-details" in u:
            return 2
        if any(x in u for x in ["onlinesbimf", "esoa", "forms", "smart-statement", "ways-to-invest", "nri-corner"]):
            return 3
        if any(x in u for x in ["mutualfundssahihai", "sebi.gov.in"]):
            return 4
        return 5

    def _lookup_fact_card(self, scheme_name: str, fact_type: Optional[str]) -> Optional[RetrievalResult]:
        """Query the structured fact cards table."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        # Simple name matching (could be improved with fuzzy matching)
        try:
            cursor.execute("""
                SELECT * FROM scheme_fact_cards 
                WHERE scheme_name LIKE ? OR ? LIKE '%' || scheme_name || '%'
            """, (f"%{scheme_name}%", scheme_name))
            row = cursor.fetchone()
            
            if not row:
                return None

            # Map fact_type to columns
            mapping = {
                "expense_ratio": "expense_ratio_regular",
                "exit_load": "exit_load",
                "min_sip": "minimum_sip",
                "min_lumpsum": "minimum_lumpsum",
                "benchmark": "benchmark_index",
                "riskometer": "riskometer",
                "lock_in": "lock_in_period"
            }

            col = mapping.get(fact_type)
            if col and row[col]:
                content = f"The {fact_type.replace('_', ' ')} for {row['scheme_name']} is {row[col]}."
                return RetrievalResult(
                    source="fact_card",
                    content=content,
                    metadata={
                        "source_url": row["source_url"],
                        "scheme_name": row["scheme_name"],
                        "fact_type": fact_type
                    }
                )
        except Exception as e:
            logger.error("Fact card lookup failed: %s", e)
        finally:
            conn.close()
        
        return None

    def _search_vectors(self, query: str, scheme_name: Optional[str] = None) -> List[RetrievalResult]:
        """Perform semantic search in Chroma Cloud with metadata filtering."""
        
        # Generate query embedding
        query_vec = self.model.encode([query], normalize_embeddings=True)[0].tolist()
        
        # Prepare filter
        where_filter = {}
        if scheme_name:
            where_filter["scheme_name"] = scheme_name

        try:
            # Query the vector store
            query_response = self.vs.query(
                query_embeddings=[query_vec],
                n_results=3,
                where=where_filter if where_filter else None
            )

            results = []
            if query_response and query_response['documents']:
                count = len(query_response['documents'][0])
                logger.info("Found %d vector results for query (Scheme: %s)", count, scheme_name)
                for i in range(count):
                    results.append(RetrievalResult(
                        source="vector_search",
                        content=query_response['documents'][0][i],
                        metadata=query_response['metadatas'][0][i],
                        score=query_response['distances'][0][i]
                    ))
            else:
                logger.warning("No vector results found in Chroma Cloud for query.")
            return results
        except Exception as e:
            logger.error("Vector search failed: %s", e)
            return []

# Testing code
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    retriever = Retriever()
    
    # Test 1: Fact card hit
    print("--- Test 1: Fact Card Hit ---")
    res1 = retriever.retrieve("What is the exit load?", "scheme_fact", "SBI Large Cap Fund", "exit_load")
    for r in res1:
        print(f"Source: {r.source} | Content: {r.content}")

    # Test 2: Vector search
    print("\n--- Test 2: Vector Search ---")
    res2 = retriever.retrieve("How to download statement?", "process_help")
    for r in res2:
        print(f"Source: {r.source} | Content: {r.content[:100]}...")
