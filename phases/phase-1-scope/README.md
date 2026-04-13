# Phase 1 — Scope Freeze and Corpus Setup

**Status: ✅ Complete**
**Deliverable:** [`corpus/source-manifest.md`](../../corpus/source-manifest.md)

## What Was Done

- AMC confirmed: SBI Mutual Fund
- 4 schemes confirmed (Large Cap, Flexi Cap, ELSS, Hybrid)
- All 20 URLs validated — HTTP 200 OK on all
- Domain allowlist finalized (7 domains)
- Crawl priority assigned P1–P4
- SPA pages flagged for Playwright extraction
- Source manifest file created

## Key Files

| File | Description |
|---|---|
| `corpus/source-manifest.md` | Full 20-URL manifest with status, priority, and access notes |
| `config/url_manifest.py` | Python config consumed by scraping service |
