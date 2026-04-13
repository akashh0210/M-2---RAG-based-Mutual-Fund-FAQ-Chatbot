"""
pipeline/chunk.py
Phase 3 — Chunking Service

Processes cleaned text from Phase 2 into semantically coherent units.
Strategies applied based on document_type:
  - scheme_page: Section-boundary splitting
  - service: Step-and-paragraph splitting
  - portal/category/campaign: Paragraph splitting
  - sebi/amfi: Topic-section splitting
  - catalogue: Link extraction only (stored in fact cards, not as chunks)

Every chunk is PII-redacted and deduplicated via content hash.
"""

import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone

from pipeline.models import get_connection, insert_chunk, get_source_document, \
    upsert_source_document
from pipeline.pii_guard import scan_and_redact
from pipeline.tokenizer import get_token_count, get_tokens, decode_tokens

logger = logging.getLogger("pipeline.chunk")

# ── Configuration ─────────────────────────────────────────────────────────────
CHUNK_OVERLAP = 50          # tokens
TARGET_CHUNK_SIZE = 400     # tokens
MAX_CHUNK_SIZE = 600        # tokens

RAW_DIR = "data/raw"

# ── Main Entry Point ──────────────────────────────────────────────────────────

def run_chunking() -> None:
    """Implement full chunking logic for all active/updated sources."""
    logger.info("=" * 70)
    logger.info("Chunking run started")
    logger.info("=" * 70)

    conn = get_connection()
    cursor = conn.cursor()

    # Get sources that need chunking:
    # 1. status = 'updated' (just scraped new content)
    # 2. chunk_count = 0 (never chunked before)
    cursor.execute("""
        SELECT source_id, document_type, scheme_name, official_url, status
        FROM source_documents
        WHERE status IN ('updated', 'active', 'unchanged', 'success') AND chunk_count = 0
    """)
    sources = cursor.fetchall()

    if not sources:
        logger.info("No active/updated sources found for chunking")
        conn.close()
        return

    summary = {"processed": 0, "total_chunks": 0, "pii_redacted": 0}

    for src in sources:
        src_dict = dict(src)
        chunk_count, pii_found = _chunk_one(conn, src_dict)
        summary["processed"] += 1
        summary["total_chunks"] += chunk_count
        if pii_found:
            summary["pii_redacted"] += 1

    logger.info("─" * 70)
    logger.info(
        "Chunking complete | processed=%d sources | total_chunks=%d | pii_redacted=%d",
        summary["processed"], summary["total_chunks"], summary["pii_redacted"]
    )

    conn.close()


# ── Internal Logic ────────────────────────────────────────────────────────────

def _chunk_one(conn, src: dict) -> tuple[int, bool]:
    """Process a single source document into chunks."""
    source_id = src["source_id"]
    doc_type = src["document_type"]
    scheme_name = src["scheme_name"]
    url = src["official_url"]

    logger.info("Chunking %s | type=%s | %s", source_id, doc_type, url)

    # Catalogues are handled via link extraction in factsheet logic, not chunks
    if doc_type == "catalogue":
        logger.info("  Skip: catalogue page (handled via links extraction)")
        return 0, False

    filepath = os.path.join(RAW_DIR, f"{source_id}.txt")
    if not os.path.exists(filepath):
        logger.warning("  Raw file not found: %s", filepath)
        return 0, False

    with open(filepath, "r", encoding="utf-8") as f:
        # Skip header lines in raw text file
        content_lines = f.readlines()
        content = "".join([line for line in content_lines if not line.startswith("#") and not line.startswith("---")])

    # 1. Split into raw segments based on document strategy
    segments = _split_into_segments(content, doc_type)

    # 2. Process segments into finalized chunks (handle size & PII)
    chunks = []
    pii_found_any = False

    for i, segment in enumerate(segments):
        # Redact PII (second pass protection)
        text, pii_alert, pii_types = scan_and_redact(segment["text"])
        if pii_alert:
            pii_found_any = True

        chunk_id = str(uuid.uuid4())
        chunk_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        chunk_data = {
            "chunk_id": chunk_id,
            "source_id": source_id,
            "run_id": os.environ.get("INGEST_RUN_ID"),
            "amc_name": "SBI Mutual Fund",
            "scheme_name": scheme_name,
            "document_type": doc_type,
            "section_title": segment.get("title"),
            "chunk_text": text,
            "token_count": get_token_count(text),
            "char_count": len(text),
            "overlap_tokens": CHUNK_OVERLAP,
            "chunk_index": i,
            "total_chunks_in_source": len(segments),
            "source_url": url,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": chunk_hash,
            "pii_redacted": int(pii_alert),
            "pii_alert_types": json.dumps(pii_types) if pii_types else None,
            "embedding_status": "pending",
            "priority_rank": 1
        }
        
        insert_chunk(conn, chunk_data)
        chunks.append(chunk_data)

    # Update source with verified chunk count
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE source_documents SET chunk_count = ? WHERE source_id = ?",
        (len(chunks), source_id)
    )
    conn.commit()

    logger.info("  ✓ Created %d chunks", len(chunks))
    return len(chunks), pii_found_any


def _split_into_segments(text: str, doc_type: str) -> list[dict]:
    """Applies splitting strategies based on the page type."""
    segments = []

    if doc_type == "scheme_page":
        # Section-boundary splitting
        # Look for headers or specific keyword boundaries (all cap sections)
        # Placeholder for complex section logic: split on multi-newlines first
        lines = text.split("\n\n")
        current_title = "General"
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Detect potential titles (short lines, camel case or all caps)
            if len(line) < 60 and (line.isupper() or ":" in line):
                current_title = line.strip(":")
                continue
            
            segments.append({"title": current_title, "text": line})

    elif doc_type in ["service", "amfi", "sebi"]:
        # Step-and-paragraph splitting
        # Split on numbered lists or bullets
        lines = re.split(r'\n(?=\d\.|\*|\-)', text)
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                segments.append({"title": f"Step/Topic {i+1}", "text": line})

    else:
        # Standard paragraph splitting for all others
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for p in paragraphs:
            segments.append({"title": None, "text": p})

    # Basic Post-processing: Merge very small segments (< 30 tokens)
    merged = []
    current = None
    
    for seg in segments:
        if current is None:
            current = seg
            continue
            
        if get_token_count(current["text"]) < 50:
            current["text"] += "\n" + seg["text"]
            if seg["title"]: current["title"] = seg["title"]
        else:
            merged.append(current)
            current = seg
            
    if current:
        merged.append(current)

    return merged


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_chunking()
