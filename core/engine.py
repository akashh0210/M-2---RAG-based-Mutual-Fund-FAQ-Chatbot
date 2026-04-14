"""
core/engine.py
Phase 4 — RAG Execution Engine

Orchestrates the Intent Classification, Retrieval, and Policy Enforcement steps.
This is the main entry point for processing a user query before generation.
"""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

from core.classifier import LocalIntentClassifier, QueryIntent
from core.retriever import Retriever, RetrievalResult
from core.policy import PolicyEngine

logger = logging.getLogger("core.engine")

# ── Result Schema ─────────────────────────────────────────────────────────────

class EngineResult(BaseModel):
    query: str
    intent: QueryIntent
    evidence: Optional[RetrievalResult] = None
    refusal_message: Optional[str] = None
    is_refused: bool = False

# ── Service Class ─────────────────────────────────────────────────────────────

class RAGEngine:
    def __init__(self):
        self.classifier = LocalIntentClassifier()
        self.retriever = Retriever()
        self.policy = PolicyEngine()

    def process_query(self, query: str) -> EngineResult:
        """Process a user query through the Phase 4 pipeline."""
        
        logger.info("Processing query: %s", query)

        # 1. Intent Classification
        intent = self.classifier.classify(query)
        logger.info("Detected intent: %s (Scheme: %s)", intent.intent, intent.scheme_name)

        # 2. Policy Check (Refusal Triggers)
        refusal_msg = self.policy.get_refusal_message(intent.intent)
        if refusal_msg:
            return EngineResult(
                query=query,
                intent=intent,
                refusal_message=refusal_msg,
                is_refused=True
            )

        # 3. Retrieval (Hybrid)
        # We only reach here if intent is scheme_fact or process_help
        results = self.retriever.retrieve(
            query=query,
            intent=intent.intent,
            scheme_name=intent.scheme_name,
            fact_type=intent.fact_type
        )

        # Select the best evidence piece
        best_evidence = results[0] if results else None

        return EngineResult(
            query=query,
            intent=intent,
            evidence=best_evidence,
            is_refused=False
        )

# ── CLI Test Tool ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    engine = RAGEngine()
    
    # Use command line arg if provided, otherwise default examples
    query = sys.argv[1] if len(sys.argv) > 1 else "What is the exit load for SBI Large Cap Fund?"
    
    result = engine.process_query(query)
    
    print("\n" + "="*50)
    print(f"QUERY: {result.query}")
    print(f"INTENT: {result.intent.intent} (Confidence: {result.intent.confidence})")
    print("-" * 50)
    
    if result.is_refused:
        print(f"REFUSAL: {result.refusal_message}")
    elif result.evidence:
        print(f"SOURCE: {result.evidence.source}")
        print(f"URL: {result.evidence.metadata.get('source_url', 'N/A')}")
        print(f"CONTENT: {result.evidence.content}")
    else:
        print("RESULT: No relevant evidence found.")
    print("="*50 + "\n")
