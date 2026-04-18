"""
core/engine.py
Phase 4 & 6 — RAG Execution Engine

Orchestrates the Intent Classification, Retrieval, Policy Enforcement, and Answer Generation.
This is the main entry point for processing a user query.
"""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

from core.classifier import LocalIntentClassifier, QueryIntent
from core.retriever import Retriever, RetrievalResult
from core.policy import PolicyEngine
from core.composer import AnswerComposer
from pipeline.models import get_connection, get_thread_context, update_thread_context, save_message

logger = logging.getLogger("core.engine")

# ── Result Schema ─────────────────────────────────────────────────────────────

class EngineResult(BaseModel):
    query: str
    intent: QueryIntent
    evidence: Optional[RetrievalResult] = None
    answer: Optional[str] = None
    refusal_message: Optional[str] = None
    is_refused: bool = False
    thread_id: Optional[str] = None

# ── Service Class ─────────────────────────────────────────────────────────────

class RAGEngine:
    def __init__(self):
        self.classifier = LocalIntentClassifier()
        self.retriever = Retriever()
        self.policy = PolicyEngine()
        self.composer = AnswerComposer()

    def process_query(self, query: str, thread_id: Optional[str] = None) -> EngineResult:
        """Process a user query through the full Phase 7 pipeline with thread context."""
        
        logger.info("Processing query: %s (Thread: %s)", query, thread_id)
        
        conn = get_connection()
        context = get_thread_context(conn, thread_id) if thread_id else {"last_scheme_name": None, "last_route": None}

        # 1. Intent Classification
        intent = self.classifier.classify(query)
        
        # Follow-up logic: If no scheme name detected but we have one in context
        if not intent.scheme_name and context.get("last_scheme_name"):
            logger.info("No scheme detected; using last context: %s", context["last_scheme_name"])
            intent.scheme_name = context["last_scheme_name"]

        logger.info("Detected intent: %s (Scheme: %s)", intent.intent, intent.scheme_name)

        # 2. Policy Check (Refusal Triggers)
        refusal_msg = self.policy.get_refusal_message(intent.intent)
        if refusal_msg:
            answer = self.composer.compose(query, None, is_refusal=True, refusal_template=refusal_msg)
            
            if thread_id:
                save_message(conn, thread_id, "user", query)
                save_message(conn, thread_id, "assistant", answer, {"intent": intent.intent, "is_refused": True})
            
            conn.close()
            return EngineResult(
                query=query,
                intent=intent,
                answer=answer,
                refusal_message=refusal_msg,
                is_refused=True,
                thread_id=thread_id
            )

        # 3. Retrieval (Hybrid)
        results = self.retriever.retrieve(
            query=query,
            intent=intent.intent,
            scheme_name=intent.scheme_name,
            fact_type=intent.fact_type
        )

        # Select the best evidence piece
        best_evidence = results[0] if results else None

        # 4. Answer Generation (Phase 6)
        answer = self.composer.compose(query, best_evidence)

        # 5. Update Thread Context & Save (Phase 7)
        if thread_id:
            save_message(conn, thread_id, "user", query)
            meta = {
                "intent": intent.intent,
                "scheme_name": intent.scheme_name,
                "fact_type": intent.fact_type,
                "source_url": best_evidence.metadata.get("source_url") if best_evidence else None
            }
            save_message(conn, thread_id, "assistant", answer, meta)
            update_thread_context(conn, thread_id, intent.scheme_name, intent.intent)

        conn.close()
        return EngineResult(
            query=query,
            intent=intent,
            evidence=best_evidence,
            answer=answer,
            is_refused=False,
            thread_id=thread_id
        )

# ── CLI Test Tool ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    engine = RAGEngine()
    
    # Use command line arg if provided, otherwise default examples
    query = sys.argv[1] if len(sys.argv) > 1 else "What is the exit load for SBI Large Cap Fund?"
    
    result = engine.process_query(query)
    
    print("\n" + "="*80)
    print(f"QUERY: {result.query}")
    print(f"INTENT: {result.intent.intent} (Confidence: {result.intent.confidence:.2f})")
    print("-" * 80)
    
    if result.answer:
        print("ANSWER:\n")
        print(result.answer)
    elif result.is_refused:
        print(f"REFUSAL: {result.refusal_message}")
    else:
        print("RESULT: No relevant evidence found.")
    
    if result.evidence:
        print("\n" + "-" * 80)
        print(f"DEBUG - Evidence Source: {result.evidence.source}")
        print(f"DEBUG - Evidence URL: {result.evidence.metadata.get('source_url', 'N/A')}")
    
    print("="*80 + "\n")
