"""
core/classifier.py
Phase 4 — Local Intent Classification Service

Routes user queries locally using semantic similarity (BGE-Base).
No OpenAI required.
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

import torch
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("core.classifier")

# ── Intent Schema ─────────────────────────────────────────────────────────────

class QueryIntent(BaseModel):
    intent: str = Field(..., description="scheme_fact | process_help | performance_link_only | advisory_refusal | restricted_data_refusal | unsupported_query")
    scheme_name: Optional[str] = Field(None)
    fact_type: Optional[str] = Field(None)
    confidence: float = Field(0.0)
    requires_refusal: bool = Field(False)

# ── Anchor Configuration ──────────────────────────────────────────────────────

INTENT_ANCHORS = {
    "scheme_fact": [
        "What is the expense ratio?",
        "Tell me the exit load for this fund.",
        "What is the minimum SIP amount?",
        "Minimum lumpsum investment limit.",
        "Check riskometer and benchmark index.",
        "ELSS tax saver lock in period."
    ],
    "process_help": [
        "How can I download my account statement?",
        "Where to find capital gains report?",
        "Steps for KYC update and documentation.",
        "Download redemption or investment forms.",
        "NRI investment process and portal help."
    ],
    "performance_link_only": [
        "What are the latest returns or absolute growth?",
        "Past fund performance and CAGR history.",
        "How has this fund performed in 3 years?",
        "Show me the NAV growth and track record."
    ],
    "advisory_refusal": [
        "Should I invest in this specific fund?",
        "Is this fund good for my portfolio?",
        "Which mutual fund is better among these two?",
        "Compare SBI Flexicap with SBI Large Cap.",
        "Give me a recommendation for high returns.",
        "Suggested scheme for wealth creation."
    ]
}

SCHEME_MAP = {
    "SBI Large Cap": "SBI Large Cap Fund",
    "SBI Bluechip": "SBI Large Cap Fund",
    "SBI Flexicap": "SBI Flexicap Fund",
    "SBI ELSS": "SBI ELSS Tax Saver Fund",
    "SBI Tax Saver": "SBI ELSS Tax Saver Fund",
    "SBI Equity Hybrid": "SBI Equity Hybrid Fund",
    "SBI Hybrid": "SBI Equity Hybrid Fund"
}

FACT_KEYWORDS = {
    "expense_ratio": ["expense", "ter", "ratio"],
    "exit_load": ["exit", "load", "redemption fee"],
    "min_sip": ["sip", "monthly", "minimum sip"],
    "min_lumpsum": ["lump", "one time", "lumpsum"],
    "benchmark": ["benchmark", "index"],
    "riskometer": ["risk", "riskometer"],
    "lock_in": ["lock", "elss", "period"]
}

PII_PATTERNS = [
    r"[A-Z]{5}[0-9]{4}[A-Z]{1}", # PAN
    r"\d{4}\s\d{4}\s\d{4}",     # Aadhaar
    r"\d{10,12}",                # Generic Account/Mobile
    r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$" # Email
]

# ── Classifier Class ──────────────────────────────────────────────────────────

class LocalIntentClassifier:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info("Initializing Local Classifier with model: %s", model_name)
        self.model = SentenceTransformer(model_name)
        
        # Pre-compute anchor embeddings
        self.anchor_vectors = {}
        for intent, queries in INTENT_ANCHORS.items():
            self.anchor_vectors[intent] = self.model.encode(queries, normalize_embeddings=True)

    def classify(self, query: str) -> QueryIntent:
        """Classify query using local semantic similarity and pattern matching."""
        
        # 1. Check for Restricted Data (PII) first
        if any(re.search(p, query) for p in PII_PATTERNS):
            return QueryIntent(
                intent="restricted_data_refusal",
                confidence=1.0,
                requires_refusal=True
            )

        # 2. Semantic Classification
        query_vec = self.model.encode([query], normalize_embeddings=True)[0]
        
        best_intent = "unsupported_query"
        max_similarity = 0.0
        
        for intent, anchors in self.anchor_vectors.items():
            # Calculate max similarity among anchors for this intent
            similarities = util.cos_sim(query_vec, anchors)[0]
            current_max = torch.max(similarities).item()
            
            if current_max > max_similarity:
                max_similarity = current_max
                best_intent = intent

        # Threshold check
        if max_similarity < 0.5:
            best_intent = "unsupported_query"

        # 3. Scheme & Fact Extraction (Deterministic)
        detected_scheme = None
        for key, full_name in SCHEME_MAP.items():
            if key.lower() in query.lower():
                detected_scheme = full_name
                break
        
        detected_fact = None
        for ftype, keywords in FACT_KEYWORDS.items():
            if any(k in query.lower() for k in keywords):
                detected_fact = ftype
                break

        return QueryIntent(
            intent=best_intent,
            scheme_name=detected_scheme,
            fact_type=detected_fact,
            confidence=round(max_similarity, 2),
            requires_refusal=(best_intent == "advisory_refusal")
        )

# Testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    classifier = LocalIntentClassifier()
    
    test_queries = [
        "What is the expense ratio of SBI Bluechip?",
        "Should I invest in SBI Flexicap?",
        "How to download my account statement?",
        "What are the returns for SBI ELSS?",
        "Compare SBI Flexicap with SBI Large Cap.",
        "Where is the nearest branch?" # Should be unsupported
    ]
    
    print("\nLocal Classification Results:")
    for q in test_queries:
        res = classifier.classify(q)
        print(f"Q: {q}\nIntent: {res.intent} | Scheme: {res.scheme_name} | Confidence: {res.confidence}\n")
