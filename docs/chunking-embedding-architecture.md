# Chunking and Embedding Architecture
**RAG Mutual Fund FAQ Assistant — SBI Mutual Fund**
**Version: 1.0 | Created: 2026-04-13**

---

## Overview

This document details how raw scraped HTML text is transformed into searchable, semantically meaningful chunks and stored as dense vector embeddings. This pipeline runs as part of the daily GitHub Actions workflow (`daily-corpus-refresh.yml`) after the scraping step completes.

The pipeline has two sequential stages:

```
Scraped raw text
       │
       ▼
 ┌─────────────────────┐
 │   Chunking Service  │  ← python -m pipeline.chunk
 └────────┬────────────┘
          │  Normalized chunks with metadata
          ▼
 ┌─────────────────────┐
 │  Embedding Service  │  ← python -m pipeline.embed
 └────────┬────────────┘
          │  Dense vectors (768-dim)
          ▼
    Vector Store (Chroma Cloud)
```

---

## Stage 1: Chunking Service

### Objective

Split cleaned page text into self-contained, semantically coherent units that:
- Fit within the embedding model's token limit (512 tokens max per chunk)
- Carry enough context to answer a question independently
- Are tagged with metadata to enable filtered retrieval

### 1.1 Pre-Chunking Checks

Before any splitting occurs, run the following on each page's raw text:

```text
1. Confirm source_id exists in source_documents with status = `active` or `updated`
2. Confirm content_changed = true  (if unchanged → skip chunking entirely)
3. Run PII Guard (regex scan):
   - PAN pattern:     [A-Z]{5}[0-9]{4}[A-Z]
   - Aadhaar pattern: \b\d{4}\s?\d{4}\s?\d{4}\b
   - Email pattern:   [a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]+
   - Phone pattern:   (\+91|0)?[6-9]\d{9}
   - OTP pattern:     \b\d{4,8}\b (contextual — only flag if near "OTP", "pin", "code")
   If PII found → redact token → log pii_alert = true → assign chunk as pii_redacted
4. Tokenize text using tiktoken (cl100k_base) to get true token count before splitting
```

### 1.2 Chunking Strategy by Page Type

Different pages have very different content structure. The chunking strategy is tailored per `document_type`:

---

#### Scheme Detail Pages — `document_type: scheme_page`
**Priority: P1 | 4 URLs**

These pages are the primary factual source. Each visible section (Fund Details, Investment Objective, Expense Ratio, Exit Load, Riskometer, Benchmark, Minimum Investment) is treated as its own chunk.

```
Strategy: Section-boundary chunking
Target size: 200–400 tokens per chunk
Max size:    500 tokens (hard limit)
Overlap:     50 tokens (carry the section heading into next chunk for context)
Method:      Detect section headings (h2, h3, bold labels) as natural split points
             If a section exceeds 500 tokens → split further on paragraph boundaries
```

**Chunk example (Expense Ratio section):**
```json
{
  "section_title": "Expense Ratio",
  "chunk_text": "The Total Expense Ratio (TER) for SBI Large Cap Fund – Regular Plan is 1.65% per annum. The Direct Plan TER is 0.87% per annum. TER is reviewed and updated periodically as per SEBI guidelines.",
  "token_count": 52,
  "scheme_name": "SBI Large Cap Fund"
}
```

---

#### Investor Service Pages — `document_type: service`
**5 URLs: forms, smart-statement, ways-to-invest, nri-corner, half-yearly-portfolios-statements**

These pages contain step-by-step processes and FAQ-style text. Split on numbered steps, headings, and paragraph breaks.

```
Strategy: Step-and-paragraph chunking
Target size: 250–450 tokens per chunk
Max size:    500 tokens
Overlap:     75 tokens (carry last sentence of previous step for continuity)
Method:      Split on <ol>/<ul> list items, <p> tags, visible H2/H3 headings
             Group related steps (e.g., "Step 1 + Step 2") into a single chunk if total < 400 tokens
```

---

#### Catalogue / Index Pages — `document_type: catalogue`
**3 URLs: factsheets, offer-document-sid-kim, half-yearly-portfolios-statements**

For these, only links and section headings matter — not body text. Do not create semantic chunks from raw link listings.

```
Strategy: Link extraction only — NOT full-text chunking
Extract:   Scheme name + document type label + hyperlink URL per row
Output:    Stored as structured rows in source_documents (not in source_chunks)
Purpose:   Used to populate factsheet_url, kim_url, sid_url fields in scheme_fact_cards
```

---

#### Investor Portals — `document_type: portal`
**4 URLs: onlinesbimf.com, online.sbimf.com, esoa.sbimf.com, corporate.sbimf.com**

These pages have minimal factual content — mostly navigation links and process descriptions.

```
Strategy: Paragraph chunking — informational text only
Target size: 200–350 tokens
Max size:    400 tokens
Overlap:     50 tokens
Skip:        Login/transaction UI copy; button labels; promotional banners
             Any text inside <form>, <input>, <button> tags is excluded
```

---

#### Category / Campaign Pages — `document_type: category_page | campaign`
**2 URLs: hybrid-mutual-funds, balanced-advantage-fund**

```
Strategy: Informational-paragraph chunking
Target size: 200–400 tokens
Max size:    450 tokens
Overlap:     50 tokens
Skip:        CTA buttons, hero banners, promotional taglines
             Only extract: factual feature descriptions, eligibility text, process steps
```

---

#### SEBI Regulatory Page — `document_type: sebi`
**1 URL**

```
Strategy: Topic-section chunking
Target size: 300–500 tokens
Max size:    600 tokens
Overlap:     75 tokens
Method:      Split on numbered provisions and table rows
```

---

#### AMFI Education Page — `document_type: amfi`
**1 URL**

```
Strategy: Topic-section chunking
Target size: 300–500 tokens
Max size:    600 tokens
Overlap:     75 tokens
Purpose:     Used exclusively for the refusal flow educational links — not retrieved for factual answers
```

---

### 1.3 Chunk Metadata Schema

Every chunk written to `source_chunks` carries the following metadata:

```json
{
  "chunk_id": "uuid-v4",
  "source_id": "uuid — references source_documents.source_id",
  "run_id": "uuid — references the scraping_logs run that produced this chunk",
  "amc_name": "SBI Mutual Fund",
  "scheme_name": "SBI Large Cap Fund | null",
  "document_type": "scheme_page | service | catalogue | portal | category_page | campaign | sebi | amfi",
  "section_title": "Expense Ratio | null",
  "chunk_text": "string — cleaned, PII-redacted text",
  "token_count": 187,
  "char_count": 923,
  "overlap_tokens": 50,
  "chunk_index": 3,
  "total_chunks_in_source": 11,
  "source_url": "https://www.sbimf.com/sbimf-scheme-details/...",
  "crawled_at": "2026-04-13T03:45:00Z",
  "content_hash": "sha256-hex — hash of chunk_text",
  "pii_redacted": false,
  "embedding_status": "pending | done | skipped",
  "priority_rank": 1
}
```

### 1.4 Chunk Deduplication

To avoid re-embedding unchanged chunks across daily runs:

```text
1. For each new chunk, compute SHA-256 of chunk_text
2. Query source_chunks for existing chunk with same source_id + chunk_index
3. Compare content_hash:
   - Match   → set embedding_status = `skipped` (existing embedding is still valid)
   - No match → set embedding_status = `pending` (must be re-embedded)
4. Delete orphaned chunks (source_id exists but crawl removed the section)
```

### 1.5 Chunking Service Output

```text
- source_chunks table updated with new/changed chunks (embedding_status = pending)
- Unchanged chunks marked as skipped
- Orphaned chunks deleted
- Summary log: total chunks processed, new, updated, skipped, deleted, pii_redacted
```

---

## Stage 2: Embedding and Vector Storage

### Objective

Convert each `pending` chunk's text into a dense vector representation, then store the vector alongside the chunk metadata in **Chroma Cloud**. Chroma Cloud serves as our primary managed semantic search engine, while SQLite remains the source of truth for metadata.

### 2.1 Embedding Model

| Property | Value |
|---|---|
| Primary model | `BAAI/bge-base-en-v1.5` (Local) — 768 dimensions |
| Token limit | 512 tokens max (BERT-based) |
| Normalization | L2-normalized before storage |
| Cost control | Zero API cost (runs locally on GitHub Runner) |

**Why `bge-base-en-v1.5`:**
- Top-tier performance on the MTEB leaderboard for retrieval tasks.
- 768 dimensions → excellent balance between retrieval depth and storage efficiency.
- Instruction-aware: Can be optimized with prefixes (though pass-through is default).
- Zero dependency on external APIs (consistent performance).

### 2.2 Batch Embedding

To respect rate limits and minimize latency, chunks are embedded in batches:

```python
# pipeline/embed.py — batch embedding logic

BATCH_SIZE = 100          # OpenAI: up to 2048 inputs per request, cap at 100 for reliability
RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5

def embed_pending_chunks(db_session):
    chunks = db_session.query(Chunk).filter_by(embedding_status="pending").all()

    for batch in chunks_in_batches(chunks, BATCH_SIZE):
        texts = [chunk.chunk_text for chunk in batch]

        for attempt in range(RETRY_ATTEMPTS):
            try:
                response = openai.embeddings.create(
                    input=texts,
                    model="text-embedding-3-small"
                )
                vectors = [item.embedding for item in response.data]
                break
            except openai.RateLimitError:
                time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
            except openai.APIError:
                # fall back to local model
                vectors = local_model.encode(texts, normalize_embeddings=True).tolist()
                break

        for chunk, vector in zip(batch, vectors):
            chunk.embedding = vector                   # stored in pgvector column
            chunk.embedding_model = "text-embedding-3-small"
            chunk.embedding_status = "done"
            chunk.embedded_at = datetime.utcnow()

    db_session.commit()
```

### 2.3 Vector Storage — Chroma Cloud Schema

Vectors are stored in a managed Chroma Cloud collection. Unlike local storage, Chroma Cloud handles durability and availability automagically:

- **IDs**: UUIDs (mapped exactly to `chunk_id` in SQLite)
- **Embeddings**: 768-dim BGE vectors
- **Documents**: The full `chunk_text` for citation/display
- **Metadatas**:
    - `source_id`: For source filtering
    - `scheme_name`: For scheme-specific retrieval
    - `document_type`: For intent-based filtering
    - `source_url`: For immediate citation

**Why Chroma Cloud over Local ChromaDB:**
- **Zero-Maintenance**: No need to manage local parquet files or sqlite3 databases.
- **Scaling**: Optimized for concurrent retrieval across multiple user threads.
- **Deployment-Ready**: Shared state accessible from both the scraper (local) and the API (Cloud).

### 2.4 Retrieval-Time Vector Query (ChromaDB API)

When the retrieval pipeline runs a semantic search, it uses ChromaDB's built-in filtering:

```python
# Retrieval example
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5,
    where={
        "$and": [
            {"scheme_name": "SBI Flexicap Fund"},
            {"document_type": "scheme_page"}
        ]
    }
)
```

For `process_help` queries (statement download, forms, NRI), the `document_type` filter opens to `service | portal`.

### 2.5 Embedding Service Output

```text
- All pending chunks embedded and stored in pgvector
- embedding_status updated: pending → done (or failed if all retries exhausted)
- embedded_at timestamp recorded for each chunk
- Summary log: chunks embedded, model used (openai / local), batches, duration, cost estimate
```

---

## End-to-End Pipeline Summary

```text
GitHub Actions triggers at 03:45 UTC (09:15 IST)
│
├── pipeline.scrape
│     Fetch 20 URLs → strip boilerplate → PII guard → content hash → write raw text
│
├── pipeline.chunk
│     Per document_type strategy → section/paragraph/step splitting
│     → PII re-check at chunk level → dedup via hash → write to source_chunks (status=pending)
│
├── pipeline.embed
│     Batch embed pending chunks (100/batch) → store vectors in pgvector
│     → fallback to MiniLM if OpenAI API unavailable
│
└── pipeline.finalize
      Update source_documents status → write scraping_logs run record → emit job summary
```

---

## Chunking and Embedding Parameters — Reference Table

| Parameter | Value | Rationale |
|---|---|---|
| Max tokens per chunk | 500 (scheme/service), 600 (SEBI/AMFI) | Fits within embedding model limit; avoids truncation |
| Overlap tokens | 50–75 | Preserves context at chunk boundaries |
| Min chunk size | 50 tokens | Discard near-empty chunks (headings only) |
| Batch size (embedding) | 100 chunks per batch | Local inference |
| Embedding dimensions | 768 (`bge-base-en-v1.5`) | High-accuracy local retrieval |
| Vector Store | Chroma Cloud (Managed) | Zero local disk footprint |
| Similarity metric | Cosine | Standard for BGE |
| Dedup method | SHA-256 hash of chunk_text | Skip re-embedding unchanged chunks |
| PII guard scope | Pre-chunk (page level) + post-chunk (chunk level) | Double-check ensures no PII slips into index |
| Retry attempts (embedding) | 3 (with exponential back-off) | Handles transient OpenAI API errors |

---

## Files in the Pipeline

| File | Responsibility |
|---|---|
| `pipeline/scrape.py` | Fetch URLs, strip HTML, PII guard, compute page hash |
| `pipeline/chunk.py` | Split text by page type, deduplicate, write to `source_chunks` |
| `pipeline/embed.py` | Batch embed pending chunks, write vectors to pgvector |
| `pipeline/finalize.py` | Update source status, write `scraping_logs` run record |
| `pipeline/pii_guard.py` | Shared regex patterns for PAN, Aadhaar, phone, email, OTP |
| `pipeline/tokenizer.py` | Shared tiktoken wrapper (`cl100k_base`) for token counting |
| `.github/workflows/daily-corpus-refresh.yml` | GitHub Actions scheduler — 03:45 UTC daily |

---

## Known Limitations

- Angular SPA pages (`esoa`, `corporate`) require Playwright in the GitHub Actions runner — install time adds ~60s to the workflow
- Scheme detail pages on SBIMF may render key fact tables via JavaScript; if Playwright is not used for these pages, some facts may be missed
- IVFFlat index requires a `VACUUM ANALYZE` after large daily updates to maintain query performance; add to the `finalize` step
- `all-MiniLM-L6-v2` vectors (384-dim) are not compatible with the 1536-dim IVFFlat index; a separate index is needed if the fallback model is used frequently
