"""
pipeline/run_pipeline.py
Master orchestrator for the SBI-MF RAG Ingestion Pipeline.

Runs all Phase 2 and Phase 3 steps in sequence:
  1. Scrape URLs -> Clean text
  2. Perform Structured Fact Extraction (Scheme Cards)
  3. Chunk Cleaned Text
  4. Generate and Store Embeddings
  5. Finalize run and update status

Usage:
  python -m pipeline.run_pipeline
"""

import logging
import os
import sys
import uuid
import traceback
from datetime import datetime, timezone

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline.scrape import run_daily_scrape
from pipeline.fact_extractor import run_fact_extraction
from pipeline.chunk import run_chunking
from pipeline.embed import run_embedding
from pipeline.finalize import finalize_run
from pipeline.models import mask_url

# ── Global ID for the run ─────────────────────────────────────────────────────
RUN_ID = str(uuid.uuid4())
os.environ["INGEST_RUN_ID"] = RUN_ID

# Ensure logs directory and vector_db directory exists
os.makedirs("logs", exist_ok=True)
os.makedirs("vector_db", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join("logs", f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"))
    ]
)
logger = logging.getLogger("pipeline.orchestrator")


def execute_full_pipeline() -> None:
    """Run the end-to-end ingestion refresh."""
    start_time = datetime.now(timezone.utc)
    
    # CI Environment Debug Info
    print("\n" + "=" * 80)
    print(" CI ENVIRONMENT CHECK ")
    print("-" * 80)
    print(f"  GROQ_API_KEY      : {'LOADED' if os.getenv('GROQ_API_KEY') else 'MISSING'}")
    print(f"  CHROMA_API_KEY    : {'LOADED' if os.getenv('CHROMA_API_KEY') else 'MISSING'}")
    print(f"  CHROMA_TENANT     : {os.getenv('CHROMA_TENANT', 'MISSING')}")
    print(f"  CHROMA_DATABASE   : {os.getenv('CHROMA_DATABASE', 'MISSING')}")
    print(f"  DATABASE_URL      : {mask_url(os.getenv('DATABASE_URL', 'Using SQLite'))}")
    print(f"  GITHUB_ACTIONS    : {os.getenv('GITHUB_ACTIONS', 'false')}")
    print("=" * 80 + "\n")
    sys.stdout.flush()

    logger.info("=" * 80)
    logger.info(" SBI-MF RAG INGESTION PIPELINE | RUN_ID: %s ", RUN_ID)
    logger.info("=" * 80)

    try:
        # Step 1: Scrape
        logger.info("[STEP 1/5] Scraping 20 URLs...")
        run_daily_scrape()

        # Step 2: Extract Facts (Deterministic Layer)
        logger.info("[STEP 2/5] Extracting deterministic facts (Scheme Fact Cards)...")
        run_fact_extraction()

        # Step 3: Chunk
        logger.info("[STEP 3/5] Chunking cleaned text...")
        run_chunking()

        # Step 4: Embed
        logger.info("[STEP 4/5] Generating vector embeddings (OpenAI/Local)...")
        run_embedding()

        # Step 5: Finalize
        logger.info("[STEP 5/5] Finalizing run status...")
        finalize_run()

    except Exception as e:
        logger.error("!!! PIPELINE CRITICAL FAILURE !!!")
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

    duration = datetime.now(timezone.utc) - start_time
    logger.info("=" * 80)
    logger.info(" PIPELINE COMPLETED SUCCESSFULLY | Duration: %s", duration)
    logger.info("=" * 80)


if __name__ == "__main__":
    execute_full_pipeline()
