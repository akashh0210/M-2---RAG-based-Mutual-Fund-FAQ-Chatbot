# Phase 2 — Ingestion: Scheduler and Scraping Service

**Status: ✅ Complete**

## What Was Built

### Scheduler (GitHub Actions)
- Cron: `45 3 * * *` → 09:15 AM IST daily
- Manual trigger via `workflow_dispatch`
- File: `.github/workflows/daily-corpus-refresh.yml`

### Scraping Service
- Fetches all 20 approved URLs in P1→P4 order
- `requests` + `BeautifulSoup` for static HTML
- `Playwright` (headless Chromium) for Angular SPA pages (`esoa`, `corporate`)
- Strips nav/footer/CTAs/cookie banners
- PII guard (page-level scan + redact)
- SHA-256 content hash → skip re-processing unchanged pages
- 3 retries per URL; 1s rate limit delay between requests

## Key Files

| File | Description |
|---|---|
| `.github/workflows/daily-corpus-refresh.yml` | GitHub Actions scheduler + 4-step pipeline |
| `pipeline/scrape.py` | Full scraping service implementation |
| `pipeline/pii_guard.py` | PII detection and redaction (PAN, Aadhaar, email, phone, OTP) |
| `pipeline/models.py` | SQLite / PostgreSQL schema and CRUD helpers |
| `pipeline/finalize.py` | Run finalization — marks sources active, writes summary |
| `config/url_manifest.py` | 20-URL config with fetch method and priority |
| `data/raw/` | Cached cleaned text per URL (generated at runtime) |
| `data/logs/` | Per-run scrape logs and JSON summary (generated at runtime) |

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run scraping only
python -m pipeline.scrape

# Check SQLite DB
sqlite3 data/rag.db "SELECT source_id, status, chunk_count FROM source_documents;"
```

## GitHub Secrets Required (for production)

| Secret | Value |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENAI_API_KEY` | OpenAI API key (used in Phase 3 embedding) |
| `INGEST_API_KEY` | Internal API key for `/ingest/run` override |
