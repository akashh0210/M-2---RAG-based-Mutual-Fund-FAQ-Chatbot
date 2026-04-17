"""
pipeline/scrape.py
Phase 2 — Scraping Service

Fetches all 20 approved URLs in crawl-priority order (P1 → P4).
For each URL:
  1. Fetch page (requests+BS4 or Playwright for Angular SPAs)
  2. Validate HTTP status
  3. Strip nav, footer, cookie banners, CTA buttons
  4. Run PII guard (page-level scan + redact)
  5. Compute SHA-256 content hash (skip re-processing if unchanged)
  6. Write raw cleaned text to source_documents
  7. Log crawl result to scraping_logs

Run directly:   python -m pipeline.scrape
Via GitHub Actions: called as step 5 of daily-corpus-refresh.yml
"""

import hashlib
import json
import logging
import os
import sys
import re
import time
import uuid
import traceback
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Comment, Tag

from config.url_manifest import get_urls_by_priority, ALLOWED_DOMAINS
from pipeline.pii_guard import scan_and_redact
from pipeline.models import get_connection, init_db, upsert_source_document, \
    get_source_document, write_scraping_log

# ── Configuration ─────────────────────────────────────────────────────────────
RATE_LIMIT_DELAY = 1.0      # seconds between requests (be polite to AMC servers)
MAX_RETRIES = 3
REQUEST_TIMEOUT = 20        # seconds
PLAYWRIGHT_TIMEOUT = 15_000 # milliseconds

RUN_ID = os.environ.get("INGEST_RUN_ID", str(uuid.uuid4()))
RUN_TRIGGERED_BY = "scheduler" if os.environ.get("GITHUB_ACTIONS") else "manual"

LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"{LOG_DIR}/scrape_{RUN_ID}.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("pipeline.scrape")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# CSS selectors / tag names to strip before text extraction
_STRIP_TAGS = [
    "nav", "header", "footer", "script", "style", "noscript",
    "iframe", "svg", "button", "form", "input", "select", "textarea",
]
_STRIP_CLASSES_RE = re.compile(
    r"(cookie|banner|popup|modal|overlay|cta|promo|advert|breadcrumb|"
    r"social|share|sidebar|newsletter|subscribe|toll-free|whatsapp)",
    re.IGNORECASE,
)


# ── Main entry point ──────────────────────────────────────────────────────────

def run_daily_scrape() -> None:
    """Execute the full scraping pipeline over all approved URLs."""
    logger.info("=" * 70)
    logger.info("Scraping run started | run_id=%s | triggered_by=%s", RUN_ID, RUN_TRIGGERED_BY)
    logger.info("=" * 70)

    conn = get_connection()
    init_db(conn)

    urls = get_urls_by_priority()
    summary = {"total": len(urls), "success": 0, "failed": 0, "unchanged": 0, "pii_alerts": 0}

    for entry in urls:
        result = _scrape_one(conn, entry)
        summary[result["outcome"]] = summary.get(result["outcome"], 0) + 1
        if result.get("pii_alert"):
            summary["pii_alerts"] += 1
        time.sleep(RATE_LIMIT_DELAY)

    logger.info("─" * 70)
    logger.info(
        "Run complete | total=%d success=%d failed=%d unchanged=%d pii_alerts=%d",
        summary["total"], summary["success"], summary["failed"],
        summary["unchanged"], summary["pii_alerts"],
    )

    conn.close()
    _write_run_summary(summary)


# ── Per-URL scraping ──────────────────────────────────────────────────────────

def _scrape_one(conn, entry: dict) -> dict:
    """Fetch, clean, PII-check, and persist one URL."""
    url = entry["url"]
    source_id = entry["id"]
    fetch_method = entry["fetch_method"]

    logger.info(
        "[P%d] %s | method=%s | %s",
        entry["crawl_priority"], source_id, fetch_method, url,
    )

    # Validate domain is on allowlist
    domain = urlparse(url).netloc
    if domain not in ALLOWED_DOMAINS:
        logger.error("DOMAIN NOT ALLOWED: %s — skipping", domain)
        return {"outcome": "failed"}

    start_ms = _now_ms()
    http_status = None
    error_message = None
    raw_text = ""
    content_changed = False
    pii_alert = False
    pii_types = []
    status = "failed"   # default; overwritten on success

    try:
        # ── Fetch ──────────────────────────────────────────────────────────────
        if fetch_method == "playwright":
            raw_html, http_status = _fetch_with_playwright(url)
        else:
            raw_html, http_status = _fetch_with_requests(url)

        if http_status != 200:
            raise ValueError(f"HTTP {http_status}")

        # ── Extract visible text ──────────────────────────────────────────────
        raw_text = _extract_text(raw_html, entry["document_type"])

        # ── PII guard (page level) ────────────────────────────────────────────
        raw_text, pii_alert, pii_types = scan_and_redact(raw_text)
        if pii_alert:
            logger.warning("PII detected in %s | types=%s", url, pii_types)

        # ── Content hash (skip re-processing if unchanged) ────────────────────
        new_hash = _sha256(raw_text)
        existing = get_source_document(conn, source_id)
        content_changed = (existing is None) or (existing.get("content_hash") != new_hash)

        status = "updated" if content_changed else "unchanged"
        outcome = "success" if content_changed else "unchanged"

        # ── Persist source_documents ──────────────────────────────────────────
        now_iso = _now_iso()
        upsert_source_document(conn, {
            "source_id": source_id,
            "scheme_name": entry.get("scheme_name"),
            "document_type": entry["document_type"],
            "official_url": url,
            "domain": domain,
            "crawl_priority": entry["crawl_priority"],
            "fetch_method": fetch_method,
            "last_crawled_at": now_iso,
            "last_verified_at": now_iso,
            "status": status,
            "content_hash": new_hash,
            "http_status": http_status,
            "chunk_count": 0,   # updated after chunking step
            "access_notes": entry.get("access_notes", ""),
        })

        # ── Cache raw text to disk (for chunk step) ───────────────────────────
        if content_changed:
            _save_raw_text(source_id, raw_text, entry)
            logger.info(
                "  ✓ %s | http=%d | chars=%d | changed=%s | pii=%s",
                source_id, http_status, len(raw_text), content_changed, pii_alert,
            )
        else:
            logger.info("  → %s | UNCHANGED (hash match — skipping re-chunk)", source_id)

    except Exception as exc:
        error_message = str(exc)
        http_status = http_status or 0
        outcome = "failed"
        status = "failed"
        logger.error("  ✗ %s | error=%s", source_id, error_message)

        # Still upsert with failed status so the log is complete
        upsert_source_document(conn, {
            "source_id": source_id,
            "scheme_name": entry.get("scheme_name"),
            "document_type": entry["document_type"],
            "official_url": url,
            "domain": domain,
            "crawl_priority": entry["crawl_priority"],
            "fetch_method": fetch_method,
            "last_crawled_at": _now_iso(),
            "last_verified_at": _now_iso(),
            "status": "failed",
            "content_hash": None,
            "http_status": http_status,
            "chunk_count": 0,
            "access_notes": entry.get("access_notes", ""),
        })

    duration_ms = _now_ms() - start_ms

    write_scraping_log(conn, {
        "log_id": str(uuid.uuid4()),
        "run_id": RUN_ID,
        "run_triggered_by": RUN_TRIGGERED_BY,
        "run_at": _now_iso(),
        "source_id": source_id,
        "url": url,
        "crawl_priority": entry["crawl_priority"],
        "http_status": http_status,
        "fetch_method": fetch_method,
        "source_status": status,
        "chunk_count": 0,
        "content_changed": int(content_changed),
        "pii_alert": int(pii_alert),
        "pii_alert_types": json.dumps(pii_types) if pii_types else None,
        "duration_ms": duration_ms,
        "error_message": error_message,
    })

    return {
        "outcome": outcome,
        "pii_alert": pii_alert,
        "source_id": source_id,
    }


# ── Fetch helpers ─────────────────────────────────────────────────────────────

def _fetch_with_requests(url: str) -> tuple[str, int]:
    """Fetch a static HTML page using requests with retry logic."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            if response.status_code == 200:
                return response.text, 200
            logger.warning("Attempt %d/%d | HTTP %d | %s", attempt, MAX_RETRIES, response.status_code, url)
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
        except requests.RequestException as e:
            logger.warning("Attempt %d/%d | %s | %s", attempt, MAX_RETRIES, type(e).__name__, url)
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)

    return "", 0  # all retries exhausted


def _fetch_with_playwright(url: str) -> tuple[str, int]:
    """Fetch a JavaScript-rendered page using Playwright headless Chromium."""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        logger.error("Playwright not installed — run: playwright install chromium")
        return "", 0

    with sync_playwright() as pw:
        headless_mode = os.environ.get("HEADLESS", "true").lower() == "true"
        browser = pw.chromium.launch(headless=headless_mode)
        page = browser.new_page(
            user_agent=HEADERS["User-Agent"],
            extra_http_headers={"Accept-Language": "en-IN,en;q=0.9"},
        )
        try:
            response = page.goto(url, timeout=PLAYWRIGHT_TIMEOUT, wait_until="networkidle")
            http_status = response.status if response else 0
            html = page.content()
        except PWTimeout:
            logger.error("Playwright timeout after %dms | %s", PLAYWRIGHT_TIMEOUT, url)
            html, http_status = "", 0
        finally:
            browser.close()

    return html, http_status


# ── Text extraction ───────────────────────────────────────────────────────────

def _extract_text(html: str, document_type: str) -> str:
    """
    Extract visible, factual text from raw HTML.
    Strips navigation, footer, cookie banners, and promotional copy.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove HTML comments
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Remove structural noise tags
    for tag in _STRIP_TAGS:
        for el in soup.find_all(tag):
            el.decompose()

    # Remove elements whose class/id matches promotional patterns
    # BS4 4.14+: Tag.attrs can be None on certain synthetic nodes — use safe access
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        attrs = el.attrs or {}
        classes = " ".join(attrs.get("class", []) or [])
        element_id = attrs.get("id", "") or ""
        if _STRIP_CLASSES_RE.search(classes) or _STRIP_CLASSES_RE.search(element_id):
            el.decompose()

    # For catalogue pages — only keep link text (no body prose)
    if document_type == "catalogue":
        links = soup.find_all("a", href=True)
        lines = []
        for link in links:
            text = link.get_text(strip=True)
            href = link["href"]
            if text and len(text) > 3:
                lines.append(f"{text} | {href}")
        return "\n".join(lines)

    # For all other pages — get all visible text
    text = soup.get_text(separator="\n", strip=True)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


# ── Utilities ─────────────────────────────────────────────────────────────────

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _save_raw_text(source_id: str, text: str, entry: dict) -> None:
    """Cache cleaned text to disk for the chunking step."""
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    filepath = f"{raw_dir}/{source_id}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# source_id: {source_id}\n")
        f.write(f"# url: {entry['url']}\n")
        f.write(f"# document_type: {entry['document_type']}\n")
        f.write(f"# scheme_name: {entry.get('scheme_name', '')}\n")
        f.write(f"# crawl_priority: {entry['crawl_priority']}\n")
        f.write(f"# scraped_at: {_now_iso()}\n")
        f.write("---\n")
        f.write(text)
    logger.debug("  Raw text saved → %s", filepath)


def _write_run_summary(summary: dict) -> None:
    """Write a JSON summary of the run to data/logs/."""
    path = f"{LOG_DIR}/run_summary_{RUN_ID}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"run_id": RUN_ID, "run_at": _now_iso(), **summary}, f, indent=2)
    logger.info("Run summary written → %s", path)


def _now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Allow running as module ───────────────────────────────────────────────────

if __name__ == "__main__":
    run_daily_scrape()
