"""
pipeline/fact_extractor.py
Phase 3 — Structured Fact Extraction

Extracts deterministic factual data from cleaned scheme pages into the
scheme_fact_cards table. This provides 100% accuracy for common queries like
'expense ratio' or 'min SIP' without relying on LLM retrieval alone.

Target: source_documents with document_type='scheme_page'
"""

import logging
import os
import re
from datetime import datetime, timezone

from pipeline.models import get_connection

logger = logging.getLogger("pipeline.fact_extractor")

RAW_DIR = "data/raw"

# ── Extraction Patterns ───────────────────────────────────────────────────────

# Expense Ratio
_EXPENSE_REGULAR = re.compile(r"Expense Ratio Regular in %.*?\n:\n(\d+\.\d+)", re.IGNORECASE | re.DOTALL)
_EXPENSE_DIRECT = re.compile(r"Expense Ratio Direct in %.*?\n:\n(\d+\.\d+)", re.IGNORECASE | re.DOTALL)

# Exit Load (Look for the block after the header)
_EXIT_LOAD_HEADER = re.compile(r"Exit Load\n(.*?)(?=\nBenchmark|₹|\bMin\b)", re.IGNORECASE | re.DOTALL)

# Investment Criteria (SIP/Lumpsum)
_MIN_SIP = re.compile(r"Min\.\s+Amount\s+Rs\.\n(\d+,?\d*)", re.IGNORECASE)
_MIN_LUMPSUM = re.compile(r"Min\.\s+Lumpsum\s+amount\s+Rs\.\n(\d+,?\d*)", re.IGNORECASE)
# Fallback patterns from 'Investment Criteria' section
_MIN_SIP_FALLBACK = re.compile(r"Min SIP Amount\n₹\s+(\d+,?\d*)", re.IGNORECASE)
_MIN_LUMPSUM_FALLBACK = re.compile(r"Min Lumpsum\n₹\s+(\d+,?\d*)", re.IGNORECASE)

# Riskometer
_RISKOMETER = re.compile(r"RISKOMETER\nThe risk of the scheme is\n(.*?)\n", re.IGNORECASE)
# Fallback for riskometer in FAQ section
_RISKOMETER_FAQ = re.compile(r"Riskometer level of.*?rated as a\s+(.*?)\.", re.IGNORECASE)

# Benchmark
_BENCHMARK = re.compile(r"Scheme Benchmark:\s+(.*?)\n", re.IGNORECASE)

# Lock-in (mostly for ELSS)
_LOCK_IN = re.compile(r"Is there any lock-in period.*?\n(.*?)\n", re.IGNORECASE)


# ── Main Entry Point ──────────────────────────────────────────────────────────

def run_fact_extraction() -> None:
    """Extract facts for all active scheme pages."""
    logger.info("=" * 70)
    logger.info("Fact Extraction run started")
    logger.info("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    # Get active scheme pages
    cursor.execute("""
        SELECT source_id, scheme_name, official_url
        FROM source_documents
        WHERE document_type = 'scheme_page' AND status != 'failed'
    """)
    sources = cursor.fetchall()

    if not sources:
        logger.info("No scheme pages found for fact extraction")
        conn.close()
        return

    for src in sources:
        _extract_from_source(conn, dict(src))

    conn.close()
    logger.info("Fact Extraction complete")


# ── Internal Logic ────────────────────────────────────────────────────────────

def _extract_from_source(conn, src: dict) -> None:
    source_id = src["source_id"]
    filepath = os.path.join(RAW_DIR, f"{source_id}.txt")
    
    if not os.path.exists(filepath):
        logger.warning("  Raw file not found: %s", filepath)
        return

    logger.info("Extracting facts from %s (%s)", source_id, src["scheme_name"])
    
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Extract values using patterns
    expense_reg = _parse_float(_search(_EXPENSE_REGULAR, text))
    expense_dir = _parse_float(_search(_EXPENSE_DIRECT, text))
    
    exit_load_raw = _search(_EXIT_LOAD_HEADER, text)
    exit_load = _clean_exit_load(exit_load_raw) if exit_load_raw else None
    
    min_sip = _parse_float(_search(_MIN_SIP, text) or _search(_MIN_SIP_FALLBACK, text))
    min_lumpsum = _parse_float(_search(_MIN_LUMPSUM, text) or _search(_MIN_LUMPSUM_FALLBACK, text))
    
    riskometer = (_search(_RISKOMETER, text) or _search(_RISKOMETER_FAQ, text) or "Unknown").strip()
    benchmark = _search(_BENCHMARK, text, group=1).strip() if _search(_BENCHMARK, text) else "Unknown"
    
    # ELSS specific check for lock-in
    lock_in = "None"
    if "ELSS" in src["scheme_name"] or "Long Term Equity" in text:
        lock_in = "3 Years"
    else:
        lock_in_match = _search(_LOCK_IN, text)
        if lock_in_match and "No lock-in" in lock_in_match:
            lock_in = "None"
        elif lock_in_match:
            lock_in = lock_in_match.strip()

    # 2. Persist to scheme_fact_cards
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO scheme_fact_cards
            (scheme_id, scheme_name, amc_name, expense_ratio, exit_load,
             min_sip, min_lumpsum, lock_in_period, riskometer, benchmark,
             source_url, last_updated_at)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source_id, src["scheme_name"], "SBI Mutual Fund", 
        expense_reg, exit_load, min_sip, min_lumpsum, 
        lock_in, riskometer, benchmark, src["official_url"], 
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    
    logger.info("  ✓ Facts extracted: Expense=%s, SIP=%s, Lumpsum=%s, Risk=%s", 
                expense_reg, min_sip, min_lumpsum, riskometer)


def _search(pattern: re.Pattern, text: str, group: int = 1) -> Optional[str]:
    match = pattern.search(text)
    return match.group(group) if match else None


def _parse_float(val: Optional[str]) -> Optional[float]:
    if not val: return None
    try:
        # Remove currency symbols and commas
        clean_val = val.replace("₹", "").replace(",", "").replace(" ", "").strip()
        return float(clean_val)
    except (ValueError, TypeError):
        return None


def _clean_exit_load(text: str) -> str:
    """Clean exit load block of noise terms."""
    lines = [L.strip() for L in text.split("\n") if L.strip() and L.strip().lower() != "view details"]
    return " | ".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_fact_extraction()
