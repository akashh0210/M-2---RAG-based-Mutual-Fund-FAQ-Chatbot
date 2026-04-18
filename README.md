# SBI Mutual Fund — Facts-Only RAG FAQ Assistant
   
**Product context:** Groww (UX reference)
**AMC:** SBI Mutual Fund
**Schemes:** SBI Large Cap · SBI Flexicap · SBI ELSS Tax Saver · SBI Equity Hybrid

---

## Project Status

| Phase | Description | Status |
|---|---|---|
| 1 | Scope Freeze — URL Manifest | ✅ Complete |
| 2 | Ingestion — Scheduler + Scraping Service | ✅ Complete |
| 3 | Knowledge — Chunking + Embedding + Fact Cards | ✅ Complete |
| 4 | Classification — Query Router + Refusal Engine | ✅ Complete |
| 5 | Retrieval — Hybrid Search + Citation Selector | ✅ Complete |
| 6 | Formatting — Answer Composer + One-Link Contract | 🔲 In Progress |
| 7 | API — FastAPI Backend + Multi-Thread Support | 🔲 Not Started |
| 8 | UI — Groww-Style Minimal Chat Interface | 🔲 Not Started |
| 9 | QA — Evaluation + Refusal Testing + Citation Validation | 🔲 Not Started |

---

## Folder Structure

```
M 2/
├── .github/
│   └── workflows/
│       └── daily-corpus-refresh.yml   ← GitHub Actions scheduler (09:15 AM IST)
├── corpus/
│   └── source-manifest.md             ← Phase 1: validated 20-URL manifest
├── config/
│   ├── __init__.py
│   └── url_manifest.py                ← 20 URLs with priority and fetch method
├── pipeline/
│   ├── __init__.py
│   ├── models.py                      ← SQLite / PostgreSQL schema and helpers
│   ├── pii_guard.py                   ← PII detection + redaction
│   ├── scrape.py                      ← Phase 2: scraping service ✅
│   ├── chunk.py                       ← Phase 3 stub
│   ├── embed.py                       ← Phase 3 stub
│   └── finalize.py                    ← Run finalization step
├── phases/
│   ├── phase-1-scope/
│   ├── phase-2-ingestion/
│   ├── phase-3-knowledge/
│   ├── phase-4-classification/
│   ├── phase-5-retrieval/
│   ├── phase-6-formatting/
│   ├── phase-7-api/
│   ├── phase-8-ui/
│   └── phase-9-qa/
├── docs/
│   ├── RAG-mutual-fund-faq-architecture.md
│   ├── chunking-embedding-architecture.md
│   └── ProblemStatement.md
├── data/                              ← runtime (gitignored)
│   ├── raw/                           ← cleaned text per URL
│   ├── logs/                          ← scrape run logs and summaries
│   └── rag.db                         ← SQLite DB (local dev)
└── requirements.txt
```

---

## Quick Start (Local — Phase 2)

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Run the scraping service
python -m pipeline.scrape

# 3. Inspect results
sqlite3 data/rag.db "SELECT source_id, status, http_status FROM source_documents;"
```

---

## Constraints

- **Facts-only** — no investment advice, no fund comparisons, no return calculations
- **Sources** — only 7 allowed domains; no third-party blogs or aggregators
- **Privacy** — never collect PAN, Aadhaar, account numbers, OTPs, email, or phone
- **Answer limit** — max 3 sentences, exactly one source link per answer
