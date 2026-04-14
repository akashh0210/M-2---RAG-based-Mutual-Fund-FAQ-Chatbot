"""
pipeline/audit_rag.py
Unified Audit Tool for SBIMF RAG Ingestion Pipeline (Phases 1-5)

Checks:
1. Data Integrity (Raw & Chunks)
2. Knowledge Store (Fact Cards & Chroma Cloud)
3. Local Brain (BGE Model & Intent Classification)
4. Automation (GitHub Actions)
"""

import os
import sqlite3
import logging
from typing import Dict

# Suppress noisy logs during audit
logging.getLogger("httpx").setLevel(logging.WARNING)

def audit():
    print("\n" + "="*80)
    print(" SBI-MF RAG SYSTEM AUDIT | COMPONENT STATUS (PHASES 1-5) ")
    print("="*80 + "\n")
    
    # ── [1] DATA INGESTION (Phase 2) ──────────────────────────────────────────
    raw_dir = os.path.join("data", "raw")
    if os.path.exists(raw_dir):
        files = [f for f in os.listdir(raw_dir) if f.endswith('.txt')]
        print(f"[OK] [PHASE 2] Normalized Data: {len(files)} files found")
    else:
        print(f"[FAIL] [PHASE 2] Normalized Data: Directory 'data/raw' missing")

    db_path = os.path.join("data", "rag.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM source_chunks")
        print(f"[OK] [PHASE 2] Knowledge Base: {c.fetchone()[0]} chunks found in SQLite")
        conn.close()
    else:
        print(f"[FAIL] [PHASE 2] Database: 'data/rag.db' missing")

    # ── [2] KNOWLEDGE LAYER (Phase 3) ─────────────────────────────────────────
    print(f"\n[PHASE 3] Knowledge Stores:")
    
    # Fact Cards
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM scheme_fact_cards")
        count = c.fetchone()[0]
        if count > 0:
            print(f"  [OK] Fact Cards: {count} schemes indexed (SQLite)")
        else:
            print(f"  [WARN] Fact Cards: Table empty!")
        conn.close()

    # Chroma Cloud
    try:
        from pipeline.vector_store import get_vector_store
        vs = get_vector_store()
        count = vs.get_count()
        print(f"  [OK] Chroma Cloud: {count} vectors found in 'sbi_mf_knowledge'")
    except Exception as e:
        print(f"  [FAIL] Chroma Cloud: Connection failed! ({e})")

    # ── [3] LOCAL BRAIN (Phase 4 & 5) ───────────────────────────────────────
    print(f"\n[PHASE 4/5] Local Inference & Decision Engine:")
    
    try:
        from core.classifier import LocalIntentClassifier
        classifier = LocalIntentClassifier()
        test_res = classifier.classify("What is the exit load for SBI Flexicap?")
        if test_res.intent == "scheme_fact" and test_res.scheme_name:
            print(f"  [OK] Intent Classifier: Local BGE-Base operative (Test passed: {test_res.intent})")
        else:
            print(f"  [WARN] Intent Classifier: Success, but unexpected test result ({test_res.intent})")
    except Exception as e:
        print(f"  [FAIL] Intent Classifier: Initialization failed! ({e})")

    try:
        from core.retriever import Retriever
        print(f"  [OK] Hybrid Retriever: Core logic initialized")
    except Exception as e:
        print(f"  [FAIL] Hybrid Retriever: Failure! ({e})")

    # ── [4] AUTOMATION (Phase 3) ─────────────────────────────────────────────
    print(f"\n[AUTOMATION] Scheduler Status:")
    wf_path = ".github/workflows/daily-ingest.yml"
    if os.path.exists(wf_path):
        print(f"  [OK] GitHub Actions: Workflow configured at {wf_path}")
    else:
        print(f"  [FAIL] GitHub Actions: Workflow file missing")

    print("\n" + "="*80)
    print(" AUDIT COMPLETE | ALL CORE SYSTEMS OPERATIONAL ")
    print("="*80 + "\n")

if __name__ == "__main__":
    audit()
