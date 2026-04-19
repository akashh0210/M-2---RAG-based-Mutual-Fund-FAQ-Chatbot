"""
pipeline/models.py
Database schema and helper functions for the RAG ingestion pipeline.

Storage strategy:
  - LOCAL development  → SQLite (zero setup, self-contained, stored in data/rag.db)
  - PRODUCTION (GitHub Actions → PostgreSQL) → set DATABASE_URL env var to a postgres:// URI

Tables:
  source_documents  — one row per approved URL; tracks crawl status and metadata
  source_chunks     — text chunks derived from each page; holds embedding status
  scraping_logs     — one row per pipeline run per URL

Usage:
  from pipeline.models import get_connection, init_db
  conn = get_connection()
  init_db(conn)
"""

import os
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH_DEFAULT = Path(__file__).parent.parent / "data" / "rag.db"
DB_PATH_ENV = os.environ.get("RAG_DATABASE_PATH")
DB_PATH = Path(DB_PATH_ENV) if DB_PATH_ENV else DB_PATH_DEFAULT

DATABASE_URL = os.environ.get("DATABASE_URL", "")  # fallback to SQLite if empty


def mask_url(url: str) -> str:
    """Mask the user:password part of a URL."""
    if not url:
        return ""
    if "@" in url:
        try:
            prefix, rest = url.split("://", 1)
            auth, host = rest.split("@", 1)
            return f"{prefix}://*****:*****@{host}"
        except Exception:
            return "*****"
    return url


def get_connection():
    """
    Return a database connection.
    Prefers PostgreSQL (psycopg2) if DATABASE_URL is set; falls back to SQLite.
    """
    if DATABASE_URL.startswith("postgres"):
        try:
            import psycopg2
            masked_db = mask_url(DATABASE_URL)
            logger.info("Connecting to PostgreSQL: %s", masked_db)
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except ImportError:
            logger.warning("psycopg2 not installed — falling back to SQLite")

    # SQLite fallback
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    logger.info("Connected to SQLite at %s", DB_PATH)
    return conn


def init_db(conn) -> None:
    """Create all tables if they don't exist."""
    cursor = conn.cursor()

    # ── source_documents ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_documents (
            source_id         TEXT PRIMARY KEY,
            amc_name          TEXT NOT NULL DEFAULT 'SBI Mutual Fund',
            scheme_name       TEXT,
            document_type     TEXT NOT NULL,
            official_url      TEXT NOT NULL UNIQUE,
            domain            TEXT NOT NULL,
            crawl_priority    INTEGER NOT NULL,
            fetch_method      TEXT NOT NULL DEFAULT 'requests',
            published_date    TEXT,
            last_crawled_at   TEXT,
            last_verified_at  TEXT,
            status            TEXT NOT NULL DEFAULT 'pending',
            language          TEXT NOT NULL DEFAULT 'en',
            intent_category   TEXT,
            content_hash      TEXT,
            http_status       INTEGER,
            chunk_count       INTEGER DEFAULT 0,
            access_notes      TEXT,
            created_at        TEXT NOT NULL
        )
    """)

    # ── source_chunks ─────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_chunks (
            chunk_id              TEXT PRIMARY KEY,
            source_id             TEXT NOT NULL REFERENCES source_documents(source_id),
            run_id                TEXT,
            amc_name              TEXT NOT NULL DEFAULT 'SBI Mutual Fund',
            scheme_name           TEXT,
            document_type         TEXT NOT NULL,
            section_title         TEXT,
            chunk_text            TEXT NOT NULL,
            token_count           INTEGER,
            char_count            INTEGER,
            overlap_tokens        INTEGER DEFAULT 50,
            chunk_index           INTEGER,
            total_chunks_in_source INTEGER,
            source_url            TEXT NOT NULL,
            crawled_at            TEXT,
            content_hash          TEXT,
            pii_redacted          INTEGER NOT NULL DEFAULT 0,
            pii_alert_types       TEXT,
            embedding_status      TEXT NOT NULL DEFAULT 'pending',
            embedding             TEXT,  -- Vector stored as JSON string (SQLite) or vector type (PG) [768 dimensions for BGE-Base]
            priority_rank         INTEGER,
            created_at            TEXT NOT NULL,
            updated_at            TEXT NOT NULL
        )
    """)

    # ── scheme_fact_cards ─────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheme_fact_cards (
            scheme_id             TEXT PRIMARY KEY,
            scheme_name           TEXT NOT NULL,
            amc_name              TEXT NOT NULL DEFAULT 'SBI Mutual Fund',
            expense_ratio         REAL,
            exit_load             TEXT,
            min_sip               REAL,
            min_lumpsum           REAL,
            lock_in_period        TEXT,
            riskometer            TEXT,
            benchmark             TEXT,
            source_url            TEXT,
            last_updated_at       TEXT NOT NULL
        )
    """)

    # ── threads ───────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            thread_id         TEXT PRIMARY KEY,
            last_scheme_name  TEXT,
            last_route        TEXT,
            created_at        TEXT NOT NULL,
            updated_at        TEXT NOT NULL
        )
    """)

    # ── messages ──────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id        TEXT PRIMARY KEY,
            thread_id         TEXT NOT NULL REFERENCES threads(thread_id),
            role              TEXT NOT NULL,
            content           TEXT NOT NULL,
            metadata          TEXT,
            created_at        TEXT NOT NULL
        )
    """)

    # ── scraping_logs ─────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraping_logs (
            log_id            TEXT PRIMARY KEY,
            run_id            TEXT NOT NULL,
            run_triggered_by  TEXT NOT NULL,
            run_at            TEXT NOT NULL,
            source_id         TEXT NOT NULL,
            url               TEXT NOT NULL,
            crawl_priority    INTEGER NOT NULL,
            http_status       INTEGER,
            fetch_method      TEXT NOT NULL,
            source_status     TEXT NOT NULL,
            chunk_count       INTEGER DEFAULT 0,
            content_changed   INTEGER DEFAULT 0,
            pii_alert         INTEGER DEFAULT 0,
            pii_alert_types   TEXT,
            duration_ms       INTEGER,
            error_message     TEXT
        )
    """)

    conn.commit()

    # ── MIGRATIONS ────────────────────────────────────────────────────────────
    try:
        cursor.execute("ALTER TABLE source_documents ADD COLUMN intent_category TEXT")
        conn.commit()
    except Exception:
        pass # already exists

    try:
        cursor.execute("ALTER TABLE source_chunks ADD COLUMN embedding TEXT")
        conn.commit()
    except Exception:
        pass # already exists

    logger.info("Database tables initialised")


# ── thread and message helpers ────────────────────────────────────────────────

def get_thread_context(conn, thread_id: str) -> dict:
    """Return the last scheme and route for a thread."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT last_scheme_name, last_route FROM threads WHERE thread_id = ?",
        (thread_id,)
    )
    row = cursor.fetchone()
    if row:
        return {"last_scheme_name": row["last_scheme_name"], "last_route": row["last_route"]}
    
    # Initialize thread if not exists
    now = _now()
    cursor.execute(
        "INSERT INTO threads (thread_id, created_at, updated_at) VALUES (?, ?, ?)",
        (thread_id, now, now)
    )
    conn.commit()
    return {"last_scheme_name": None, "last_route": None}


def update_thread_context(conn, thread_id: str, scheme_name: str | None, route: str | None) -> None:
    """Update metadata for a thread."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE threads 
        SET last_scheme_name = ?, last_route = ?, updated_at = ?
        WHERE thread_id = ?
    """, (scheme_name, route, _now(), thread_id))
    conn.commit()


def save_message(conn, thread_id: str, role: str, content: str, metadata: dict | None = None) -> None:
    """Save a message to the history."""
    import json
    import uuid
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (message_id, thread_id, role, content, metadata, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (str(uuid.uuid4()), thread_id, role, content, json.dumps(metadata) if metadata else None, _now()))
    conn.commit()


def get_thread_history(conn, thread_id: str, limit: int = 10) -> list[dict]:
    """Return the last N messages for a thread."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, metadata, created_at FROM messages
        WHERE thread_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (thread_id, limit))
    rows = cursor.fetchall()
    # Return in chronological order
    return [dict(row) for row in reversed(rows)]


# ── source_documents helpers ──────────────────────────────────────────────────

def upsert_source_document(conn, data: dict) -> None:
    """Insert or update a source_documents row."""
    cursor = conn.cursor()
    now = _now()
    cursor.execute("""
        INSERT INTO source_documents
            (source_id, scheme_name, document_type, official_url, domain,
             crawl_priority, fetch_method, intent_category, last_crawled_at, last_verified_at,
             status, content_hash, http_status, chunk_count, access_notes, created_at)
        VALUES
            (:source_id, :scheme_name, :document_type, :official_url, :domain,
             :crawl_priority, :fetch_method, :intent_category, :last_crawled_at, :last_verified_at,
             :status, :content_hash, :http_status, :chunk_count, :access_notes, :created_at)
        ON CONFLICT(source_id) DO UPDATE SET
            intent_category  = excluded.intent_category,
            last_crawled_at  = excluded.last_crawled_at,
            last_verified_at = excluded.last_verified_at,
            status           = excluded.status,
            content_hash     = excluded.content_hash,
            http_status      = excluded.http_status,
            chunk_count      = excluded.chunk_count
    """, {**data, "created_at": now})
    conn.commit()


def get_source_document(conn, source_id: str) -> dict | None:
    """Fetch a single source_documents row by source_id."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM source_documents WHERE source_id = ?", (source_id,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None


# ── source_chunks helpers ─────────────────────────────────────────────────────

def insert_chunk(conn, chunk: dict) -> None:
    cursor = conn.cursor()
    now = _now()
    cursor.execute("""
        INSERT OR REPLACE INTO source_chunks
            (chunk_id, source_id, run_id, amc_name, scheme_name, document_type,
             section_title, chunk_text, token_count, char_count, overlap_tokens,
             chunk_index, total_chunks_in_source, source_url, crawled_at,
             content_hash, pii_redacted, pii_alert_types, embedding_status,
             priority_rank, created_at, updated_at)
        VALUES
            (:chunk_id, :source_id, :run_id, :amc_name, :scheme_name, :document_type,
             :section_title, :chunk_text, :token_count, :char_count, :overlap_tokens,
             :chunk_index, :total_chunks_in_source, :source_url, :crawled_at,
             :content_hash, :pii_redacted, :pii_alert_types, :embedding_status,
             :priority_rank, :created_at, :updated_at)
    """, {**chunk, "created_at": now, "updated_at": now})

def update_chunk_embedding(conn, chunk_id: str, embedding: list[float]) -> None:
    """Update a chunk with its vector embedding."""
    cursor = conn.cursor()
    import json
    embedding_json = json.dumps(embedding)
    cursor.execute("""
        UPDATE source_chunks
        SET embedding = ?, embedding_status = 'done', updated_at = ?
        WHERE chunk_id = ?
    """, (embedding_json, _now(), chunk_id))
    conn.commit()


# ── scraping_logs helpers ─────────────────────────────────────────────────────

def write_scraping_log(conn, log: dict) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scraping_logs
            (log_id, run_id, run_triggered_by, run_at, source_id, url,
             crawl_priority, http_status, fetch_method, source_status,
             chunk_count, content_changed, pii_alert, pii_alert_types,
             duration_ms, error_message)
        VALUES
            (:log_id, :run_id, :run_triggered_by, :run_at, :source_id, :url,
             :crawl_priority, :http_status, :fetch_method, :source_status,
             :chunk_count, :content_changed, :pii_alert, :pii_alert_types,
             :duration_ms, :error_message)
    """, log)
    conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
