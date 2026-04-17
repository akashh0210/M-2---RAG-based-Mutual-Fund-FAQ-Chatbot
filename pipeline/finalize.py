"""
pipeline/finalize.py
Phase 2 — Finalize pipeline run.

Called as the last step of the GitHub Actions workflow.
  1. Marks all source_documents that were successfully processed as 'active'
  2. Marks sources with fetch_method failures as 'stale' if not already 'failed'
  3. Prints a structured run summary to stdout (GitHub Actions will capture it)
  4. Writes the final run record to scraping_logs

Run directly:   python -m pipeline.finalize
"""

import json
import logging
import os
import sys
import uuid
import traceback
from datetime import datetime, timezone

from pipeline.models import get_connection, write_scraping_log

RUN_ID = os.environ.get("INGEST_RUN_ID", "local")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("pipeline.finalize")


def finalize_run() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    # ── Fetch run stats from scraping_logs ────────────────────────────────────
    cursor.execute("""
        SELECT
            COUNT(*)                                AS total,
            SUM(CASE WHEN source_status IN ('active','updated','unchanged') THEN 1 ELSE 0 END) AS success,
            SUM(CASE WHEN source_status = 'failed' THEN 1 ELSE 0 END)  AS failed,
            SUM(CASE WHEN content_changed = 1 THEN 1 ELSE 0 END)       AS changed,
            SUM(pii_alert)                          AS pii_alerts,
            SUM(chunk_count)                        AS total_chunks
        FROM scraping_logs
        WHERE run_id = ?
    """, (RUN_ID,))

    row = cursor.fetchone()
    stats = dict(row) if row else {}

    # ── Mark updated sources as 'active' ──────────────────────────────────────
    cursor.execute("""
        UPDATE source_documents
        SET status = 'active', last_verified_at = ?
        WHERE source_id IN (
            SELECT source_id FROM scraping_logs
            WHERE run_id = ? AND source_status IN ('updated', 'unchanged')
        )
    """, (_now_iso(), RUN_ID))

    conn.commit()

    # ── Summary ───────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("Pipeline run FINALIZED | run_id=%s", RUN_ID)
    logger.info("  Total URLs  : %s", stats.get("total", "?"))
    logger.info("  Success     : %s", stats.get("success", "?"))
    logger.info("  Failed      : %s", stats.get("failed", 0))
    logger.info("  Changed     : %s", stats.get("changed", 0))
    logger.info("  PII alerts  : %s", stats.get("pii_alerts", 0))
    logger.info("  Total chunks: %s", stats.get("total_chunks", 0))
    logger.info("=" * 60)

    conn.close()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    finalize_run()
