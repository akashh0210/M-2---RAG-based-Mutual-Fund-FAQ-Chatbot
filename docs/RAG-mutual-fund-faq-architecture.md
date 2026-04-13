# RAG Architecture: Facts-Only Mutual Fund FAQ Assistant

## Project Positioning

| Dimension | Value |
|---|---|
| Product chosen | Groww |
| Product role | User-facing reference context only — Groww's SBI Mutual Fund AMC page is the design and UX reference |
| Factual source | Groww is **not** used as a retrieval or citation source. All factual answers come only from official public pages: SBI Mutual Fund, SEBI, and AMFI-linked education pages |
| Selected AMC | SBI Mutual Fund (SBIMF) |

---

## Milestone Goal

Build a small, compliant FAQ assistant that answers **only factual mutual fund questions**:

- Expense ratio
- Exit load
- Minimum SIP amount
- Minimum lump sum amount
- ELSS lock-in period
- Riskometer classification
- Benchmark index
- How to download account statements
- How to download capital gains statements

The assistant must:

- Answer factual queries only — no advice, no opinions, no comparisons
- Refuse advisory or opinionated questions with a polite, educational response
- Include **exactly one** clear source link per answer
- Keep every answer within **3 sentences**
- Include the footer: `Last updated from sources: <date>`
- Show a minimal UI with a welcome line, 3 example questions, and the note: `Facts-only. No investment advice.`
- Support multiple independent chat threads simultaneously

---

## Scope

### AMC

**SBI Mutual Fund** — single AMC for the full corpus and all factual retrieval.

### Schemes in Scope (4 schemes, 4 categories)

| # | Scheme Name | Category |
|---|---|---|
| 1 | SBI Large Cap Fund (formerly SBI Bluechip Fund) | Large Cap |
| 2 | SBI Flexicap Fund | Flexi Cap |
| 3 | SBI ELSS Tax Saver Fund (formerly SBI Long Term Equity Fund) | ELSS |
| 4 | SBI Equity Hybrid Fund | Hybrid |

### Other Frozen Decisions

| Decision | Value |
|---|---|
| PDF ingestion in current scope | No — web pages and HTML only; PDFs deferred to a future phase |
| Factsheet/KIM/SID reference | Identified per scheme; used as citation URLs when fetched by system |
| Refresh frequency | **Daily at 09:15 AM IST** — aligned to NSE/BSE market open; ensures NAV, expense ratio, and factsheet data are always day-fresh |

---

## Corpus Policy

### Allowed Domains

Only the following official public domains are permitted as retrieval sources. Any URL outside this list is rejected at ingestion time.

| Domain | Owner | Purpose |
|---|---|---|
| `www.sbimf.com` | SBI Mutual Fund | Scheme pages, catalogues, service pages |
| `onlinesbimf.com` | SBI Mutual Fund | Investor portal — transactions, statements |
| `online.sbimf.com` | SBI Mutual Fund | Investor portal — alternate domain |
| `esoa.sbimf.com` | SBI Mutual Fund | Electronic Statement of Account portal |
| `corporate.sbimf.com` | SBI Mutual Fund | Corporate / institutional investor portal |
| `www.sebi.gov.in` | SEBI | Regulatory disclosures, investor FAQ |
| `www.mutualfundssahihai.com` | AMFI | Investor education, refusal fallback links |

### Prohibited Sources

- Third-party blogs or news aggregators
- Unofficial fund comparison sites (e.g., Value Research, Moneycontrol, ET Money)
- Screenshots or image-only sources
- User-generated content or social media
- Groww or any other distributor platform as a factual source

### Performance Queries

Do **not** compute, summarize, or compare fund returns. For any performance-related query, return only the official factsheet link from `www.sbimf.com/factsheets`.

---

## Approved URL Manifest (20 URLs)

All 20 URLs below are non-PDF web pages and serve as the corpus anchors for the initial build.

> **Factsheet / KIM / SID note:** Official scheme factsheet, KIM, and SID documents may be fetched from the SBI MF factsheet hub (`/factsheets`) and offer-document hub (`/offer-document-sid-kim`) during ingestion for higher factual precision. The anchor list is non-PDF for the current phase, but the ingestion pipeline may follow links from these catalogue pages to retrieve authoritative PDF content in future phases. Citation links in answers should prefer SBI MF scheme pages or official document URLs where available.

### AMC — Homepage

| # | URL | Type | Purpose |
|---|---|---|---|
| 1 | https://www.sbimf.com | Homepage | Entry point, AMC overview |

### AMC — Catalogue and Index Pages

| # | URL | Type | Purpose |
|---|---|---|---|
| 2 | https://www.sbimf.com/factsheets | Factsheet catalogue | All scheme factsheets listing |
| 3 | https://www.sbimf.com/offer-document-sid-kim | SID / KIM catalogue | All SID and KIM document listing |
| 4 | https://www.sbimf.com/half-yearly-portfolios-statements | Portfolio disclosures | Half-yearly portfolio statements |
| 5 | https://www.sbimf.com/mutual-fund/hybrid-mutual-funds | Category page | Hybrid fund category overview |
| 6 | https://www.sbimf.com/campaign/balanced-advantage-fund | Campaign page | Balanced Advantage Fund information |

### AMC — Scheme Detail Pages

| # | URL | Type | Scheme |
|---|---|---|---|
| 7 | https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43 | Scheme page | SBI Large Cap Fund |
| 8 | https://www.sbimf.com/sbimf-scheme-details/sbi-flexicap-fund-39 | Scheme page | SBI Flexicap Fund |
| 9 | https://www.sbimf.com/sbimf-scheme-details/sbi-long-term-equity-fund-(previously-known-as-sbi-magnum-taxgain-scheme)-3 | Scheme page | SBI ELSS Tax Saver Fund |
| 10 | https://www.sbimf.com/sbimf-scheme-details/sbi-equity-hybrid-fund-5 | Scheme page | SBI Equity Hybrid Fund |

### AMC — Investor Service Pages

| # | URL | Type | Purpose |
|---|---|---|---|
| 11 | https://www.sbimf.com/forms | Forms library | KYC, SIP, redemption, and other forms |
| 12 | https://www.sbimf.com/smart-statement | Smart Statement | Statement download and account summary |
| 13 | https://www.sbimf.com/ways-to-invest | Ways to invest | Online, offline, and NRI investment modes |
| 14 | https://www.sbimf.com/nri-corner | NRI Corner | NRI-specific investment process and rules |

### AMC — Investor Portals

| # | URL | Type | Purpose |
|---|---|---|---|
| 15 | https://onlinesbimf.com | Investor portal | Transactions, statement download |
| 16 | https://online.sbimf.com | Investor portal | Alternate domain for online portal |
| 17 | https://esoa.sbimf.com | eSOA portal | Electronic Statement of Account access |
| 18 | https://corporate.sbimf.com | Corporate portal | Corporate / institutional investor portal |

### SEBI — Regulatory

| # | URL | Type | Purpose |
|---|---|---|---|
| 19 | https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doGetFundDetails=yes&mfId=49&type=3 | Regulatory | SEBI's official SBI MF fund details |

### AMFI — Investor Education

| # | URL | Type | Purpose |
|---|---|---|---|
| 20 | https://www.mutualfundssahihai.com/en/about-us | Education | Investor education, refusal fallback |

**Total in-scope web pages: 20** — 4 scheme categories, 7 SBIMF subdomains, full coverage of service, portal, and regulatory pages. No PDFs ingested in this phase.

---

## Core Architecture

The system is built as six logical layers:

1. **Source Layer** — Official SBIMF, SEBI, and AMFI content only. Domain allowlist enforced at ingestion time.
2. **Ingestion Layer** — HTML crawling, text extraction, normalization, chunk creation, source tracking, and metadata tagging.
3. **Knowledge Layer** — Dual store: vector database (ChromaDB for semantic search) plus structured fact cards (SQLite exact lookup).
4. **Retrieval Layer** — Query classification → route selection → hybrid search (BM25 + ChromaDB vector search) → metadata filter → reranking → deterministic citation selection.
5. **Answer Layer** — Facts-only response assembly with strict format contract, refusal policy, and privacy guards.
6. **Application Layer** — Thread-aware API, Groww-inspired minimal chat UI, audit logs, and evaluation dashboard.

---

## Phase-Wise Build Plan

### Phase 1: Scope Freeze and Corpus Setup

- Confirm AMC: SBI Mutual Fund.
- Confirm 4 schemes and categories.
- Validate all 20 URLs are accessible and not behind login walls.
- Build the source manifest (CSV/MD) with domain, type, scheme tag, and crawl priority.
- Set up domain allowlist enforcement rule.

**Output:** Approved URL manifest file. No code changes yet.

---

### Phase 2: Ingestion and Metadata Extraction

- Build a deterministic HTML crawler for each approved URL.
- Extract visible text; strip navigation chrome, cookie banners, and footer boilerplate.
- Detect and tag each page with: `amc_name`, `scheme_name`, `document_type`, `source_url`, `crawled_at`.
- Assign crawl priority: scheme pages > service pages > catalogues > portals > SEBI/AMFI.
- Log every crawl attempt with status (success / failed / stale).

**Chunking strategy by page type:**

| Page type | Strategy |
|---|---|
| Scheme detail pages | Chunk by visible section (Fund Details, Expense, Exit Load, etc.), 200–500 tokens |
| Catalogue / index pages | Extract hyperlinks and section headings only; skip raw listing tables |
| Investor service pages (forms, smart-statement, ways-to-invest, NRI corner) | Chunk by step-by-step section and visible FAQ blocks |
| Investor portals (onlinesbimf, esoa, corporate) | Extract factual process text only; skip login / transaction UI copy |
| Category / campaign pages | Chunk by informational section; skip promotional copy and CTAs |
| SEBI / AMFI pages | Chunk by topic section, 300–600 tokens |

**Corpus metadata schema:**

```json
{
  "source_id": "uuid",
  "amc_name": "SBI Mutual Fund",
  "scheme_name": "string | null",
  "document_type": "homepage | catalogue | scheme_page | service | portal | category_page | campaign | sebi | amfi",
  "official_url": "string",
  "domain": "string",
  "crawl_priority": 1,
  "published_date": "date | null",
  "last_crawled_at": "datetime",
  "last_verified_at": "datetime",
  "status": "active | stale | failed",
  "language": "en",
  "content_hash": "string"
}
```

**Chunk schema:**

```json
{
  "chunk_id": "uuid",
  "source_id": "uuid",
  "amc_name": "string",
  "scheme_name": "string | null",
  "document_type": "string",
  "section_title": "string | null",
  "chunk_text": "string",
  "token_count": 350,
  "embedding_status": "pending | done",
  "priority_rank": 1
}
```

**Output:** Normalized chunk store with metadata. Source crawl log.

---

### Scheduler and Scraping Service

#### Scheduler

#### Scheduler — GitHub Actions

The scheduler is implemented as a **GitHub Actions workflow** (`daily-corpus-refresh.yml`). It triggers every day at **09:15 AM IST (03:45 AM UTC)** via the `schedule` event using a cron expression.

This removes the need for an always-on server process; the scraping job runs inside GitHub's managed compute and pushes results back to the application database via the backend API.

```yaml
# .github/workflows/daily-corpus-refresh.yml
name: Daily Corpus Refresh — 09:15 AM IST

on:
  schedule:
    - cron: "45 3 * * *"   # 03:45 UTC = 09:15 IST every day
  workflow_dispatch:       # allows manual trigger from GitHub UI or via API

jobs:
  refresh-corpus:
    name: Fetch, Scrape, Chunk, and Embed
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium   # for Angular SPA pages

      - name: Run scraping service
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          INGEST_API_KEY: ${{ secrets.INGEST_API_KEY }}
        run: |
          python -m pipeline.scrape        # fetch + clean + PII guard

      - name: Run chunking service
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          python -m pipeline.chunk         # split text into chunks

      - name: Run embedding service
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          python -m pipeline.embed         # embed changed chunks & upsert to ChromaDB

      - name: Mark run complete
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          INGEST_API_KEY: ${{ secrets.INGEST_API_KEY }}
        run: |
          python -m pipeline.finalize      # update crawl status, write scraping_logs

      - name: Notify on failure
        if: failure()
        run: |
          echo "::error::Daily corpus refresh failed — check scraping_logs table"
```

#### GitHub Actions Scheduler — Behaviour

| Property | Value |
|---|---|
| Run time | 09:15 AM IST every day (03:45 AM UTC) |
| Cron expression | `45 3 * * *` |
| Trigger type | GitHub Actions `schedule` + `workflow_dispatch` (manual) |
| Runner | `ubuntu-latest` (GitHub-managed) |
| Max job duration | 30 minutes (`timeout-minutes: 30`) |
| Steps in order | `scrape` → `chunk` → `embed` → `finalize` |
| On success | `finalize` step marks all sources `active`; updates `last_crawled_at` |
| On failure | Job fails; GitHub notifies via error annotation; sources marked `stale`/`failed` |
| Manual override | `workflow_dispatch` — trigger via GitHub UI or `POST /repos/.../actions/workflows/.../dispatches` |
| Secrets required | `DATABASE_URL`, `OPENAI_API_KEY`, `INGEST_API_KEY` — stored in GitHub repository secrets |

---

#### Scraping Service

The scraping service is called by the scheduler (and optionally via the manual endpoint). It fetches all 20 approved URLs in crawl-priority order (P1 → P2 → P3 → P4) and feeds clean text to the ingestion pipeline.

##### Fetch Rules Per URL Type

| URL Type | Fetch Method | Reason |
|---|---|---|
| Scheme detail pages (P1) | `requests` + `BeautifulSoup` | Static HTML; no JS needed |
| Service pages — forms, ways-to-invest, NRI, smart-statement | `requests` + `BeautifulSoup` | Static HTML |
| Factsheet / SID/KIM catalogue pages | `requests` + `BeautifulSoup` | Static HTML; extract links only |
| Portals — esoa.sbimf.com, corporate.sbimf.com | `Playwright` (headless Chromium) | Angular SPA — requires JS execution |
| SEBI regulatory page | `requests` + `BeautifulSoup` | Standard HTML |
| AMFI education page | `requests` + `BeautifulSoup` | Standard HTML |

##### Scraping Service — per-URL execution flow

```text
For each URL in manifest (sorted by crawl_priority):
  1. Fetch page using appropriate method (requests or Playwright)
  2. Check HTTP status:
     - 200 → proceed
     - 3xx → follow redirect; log redirect hop
     - 4xx / 5xx → mark source as `failed`; skip; log error
  3. Extract visible text; strip:
     - Navigation menus
     - Cookie consent banners
     - Footer boilerplate
     - Promotional CTAs (buttons, ad banners)
  4. Run PII Guard:
     - Scan extracted text for PAN patterns (e.g., ABCDE1234F)
     - Scan for Aadhaar, account number, OTP, phone, email patterns
     - If found → redact and log a PII-detection alert; do NOT index the affected chunk
  5. Compute content_hash (SHA-256) of extracted text:
     - If hash matches previous crawl → mark as `unchanged`; skip re-embedding
     - If hash differs → mark as `updated`; re-chunk and re-embed
  6. Chunk text using the strategy for that page type (Phase 2 chunking table)
  7. Write chunks to source_chunks table with `embedding_status = pending`
  8. Update source_documents: `last_crawled_at`, `status`, `content_hash`
  9. Log crawl result: URL, status, chunk count, changed flag, duration (ms)
```

##### Scraping Service — key constraints

| Constraint | Rule |
|---|---|
| Domain enforcement | Only URLs in the approved manifest are crawled; no link-following outside the 7 allowed domains |
| Rate limiting | 1-second delay between each request to avoid overloading AMC servers |
| Playwright timeout | 15 seconds per page; mark as `failed` if exceeded |
| PII guard | Any chunk containing PAN / Aadhaar / account / OTP patterns is redacted and excluded from the index |
| Content hash check | Skip re-embedding unchanged pages to reduce embedding API cost |
| Max retries | 3 attempts per URL before marking as `failed` |
| smart-statement | Crawl landing text only; do NOT submit the PAN + email form |

##### Scraping logs schema

```json
{
  "run_id": "uuid",
  "run_triggered_by": "scheduler | manual_api",
  "run_at": "2026-04-13T09:15:00+05:30",
  "url": "string",
  "crawl_priority": 1,
  "http_status": 200,
  "fetch_method": "requests | playwright",
  "source_status": "active | stale | failed | unchanged",
  "chunk_count": 12,
  "content_changed": true,
  "pii_alert": false,
  "duration_ms": 1230,
  "error_message": "string | null"
}
```

**Output:** All 20 URLs fetched, cleaned, PII-checked, hashed, and chunked. Crawl log written to `scraping_logs` table.

---

### Phase 3: Structured Fact Cards and Chunk Indexing

Build two parallel knowledge stores:

#### A. Structured Fact Cards

Extract exact values from scheme pages and store in a flat table for instant lookup. Prefer SBI MF scheme pages and factsheet/KIM/SID evidence for scheme facts.

```json
{
  "scheme_id": "uuid",
  "scheme_name": "string",
  "amc_name": "SBI Mutual Fund",
  "category": "string",
  "expense_ratio_regular": "string | null",
  "expense_ratio_direct": "string | null",
  "exit_load": "string | null",
  "minimum_sip": "string | null",
  "minimum_lumpsum": "string | null",
  "benchmark_index": "string | null",
  "riskometer": "string | null",
  "lock_in_period": "string | null",
  "factsheet_url": "string | null",
  "kim_url": "string | null",
  "sid_url": "string | null",
  "statement_help_url": "string | null",
  "capital_gains_help_url": "string | null",
  "source_url": "string",
  "source_date": "date | null",
  "last_verified_at": "datetime"
}
```

#### B. Vector Database (Chroma Cloud)

Store all normalized chunks in a managed Chroma Cloud collection (`sbi_mf_knowledge`). Store 768-dim BGE vectors with full metadata (chunk_id, source_url) for filtered semantic retrieval.

#### Why both stores are needed

- **SQLite (Fact Cards)**: Faster and 100% reliable for exact facts (expense ratio, exit load, minimum SIP).
- **Chroma Cloud**: Fully managed vector database; simplifies deployment and scaling while maintaining high-performance HNSW search.
- Combining both reduces hallucinations and constrains generation to verified evidence.

**Output:** Populated fact cards table. Securely hosted Chroma Cloud collection.

---

### Phase 4: Query Classifier and Refusal Router

Every user query is classified before any retrieval is attempted.

#### Route Types

| Route | Description | Action |
|---|---|---|
| `scheme_fact` | Expense ratio, exit load, minimum SIP, riskometer, benchmark, ELSS lock-in | Structured fact lookup → vector fallback |
| `process_help` | How to download statement, capital gains, KYC forms, NRI process | Vector search on service pages |
| `performance_link_only` | Any question about returns, NAV history, CAGR, past performance | Return only official factsheet link; no computation |
| `advisory_refusal` | Should I invest, which fund is better, is this good for me | Refuse politely with one SEBI/AMFI education link |
| `restricted_data_refusal` | Query contains or requests PAN, Aadhaar, account number, OTP, phone, email | Refuse and warn never to share such information |
| `unsupported_query` | Out of scope, ambiguous, or off-topic | Ask user to rephrase as a supported factual question |

#### Intent Classifier Output

```json
{
  "intent": "scheme_fact | process_help | performance_link_only | advisory_refusal | restricted_data_refusal | unsupported_query",
  "scheme_name": "string | null",
  "fact_type": "expense_ratio | exit_load | min_sip | min_lumpsum | benchmark | riskometer | lock_in | statement | capital_gains | forms | nri | null",
  "confidence": 0.94,
  "requires_refusal": false
}
```

#### Refusal Triggers

Refuse any query that asks:

- "Should I invest in this fund?"
- "Which fund is better?"
- "Is this good for me?"
- "Which scheme should I choose?"
- Any portfolio construction, suitability, or buy/sell/hold guidance
- Any request that requires the user to share PAN, Aadhaar, OTP, account number, email, or phone

**Refusal template:**

> This assistant provides only factual information from official mutual fund sources and cannot recommend, compare, or evaluate funds for investment decisions. For investor education, please refer to: [Mutual Funds Sahi Hai](https://www.mutualfundssahihai.com/en/about-us) or [SEBI](https://www.sebi.gov.in).

**Output:** Classified route + scheme context for every query.

---

### Phase 5: Hybrid Retrieval and Citation Selector

#### Retrieval Flow

1. Parse scheme name and intent from classifier output.
2. Apply metadata filter: `amc_name`, `scheme_name`, `document_type`.
3. **If `scheme_fact`:** run structured fact card lookup first. If hit → skip vector search.
4. **If no structured hit:** run BM25 keyword search on filtered chunks.
5. Run vector similarity search on the same filtered set.
6. Merge and rerank top candidates (reciprocal rank fusion or cross-encoder reranker).
7. Select the single best evidence chunk.
8. Select exactly one citation URL using the deterministic citation priority below.

#### Citation Priority (deterministic, one URL only)

| Priority | Source |
|---|---|
| 1 | SBI MF factsheet, KIM, or SID document URL for scheme facts |
| 2 | SBI MF scheme detail page |
| 3 | SBI MF service or help page (smart-statement, forms, ways-to-invest, NRI corner) |
| 4 | SEBI or Mutual Funds Sahi Hai educational page (refusal and education flows only) |

#### Retrieval Stage Output

```json
{
  "question": "What is the minimum SIP for SBI Flexicap Fund?",
  "route": "scheme_fact",
  "scheme_name": "SBI Flexicap Fund",
  "fact_type": "min_sip",
  "selected_source_url": "https://www.sbimf.com/sbimf-scheme-details/sbi-flexicap-fund-39",
  "selected_source_date": "2026-03-31",
  "evidence_text": "...",
  "answerable": true
}
```

**Output:** Evidence chunk, selected citation URL, answerable flag.

---

### Phase 6: Answer Formatter and One-Link Contract

The language model is constrained to fill a strict response contract. It does not freely generate answers.

#### Answer Contract

1. Maximum 3 sentences.
2. Facts only — no opinion, recommendation, comparison, or interpretation.
3. Exactly one source link.
4. Footer line: `Last updated from sources: <date>`.
5. No extra references, disclaimers, or links.
6. No unsupported extrapolation beyond the evidence chunk.

#### Answer Template

```
<sentence 1>
<sentence 2 if needed>
<sentence 3 if needed>

Source: <official URL>
Last updated from sources: <date>
```

#### No-Answer Policy

If evidence is weak, missing, or ambiguous:

> I couldn't verify that from the current official sources. Please check the official scheme document or AMC support page.

#### System Prompt — Answer Composer

```text
You are a facts-only mutual fund FAQ assistant for SBI Mutual Fund schemes.
Answer only from the supplied official evidence text.
Do not provide advice, recommendations, comparisons, opinions, or suitability guidance.
Do not compute or compare returns or performance.
Use at most 3 sentences.
Include exactly one source link from the evidence.
Always end with: Last updated from sources: <date>
If evidence is insufficient or ambiguous, say you could not verify it from current official sources.
```

#### System Prompt — Refusal Router

```text
The user has asked an advisory, comparative, or restricted question.
Refuse politely and clearly.
State that this assistant provides only factual information from official mutual fund sources.
Provide exactly one educational link from SEBI or Mutual Funds Sahi Hai.
Do not provide any investment guidance or fund comparison.
```

**Output:** Formatted answer string conforming to the one-link contract.

---

### Phase 7: Backend API and Multi-Thread Support

#### Thread Model

- Every conversation is an independent thread with its own context.
- No cross-thread scheme memory.
- Follow-up questions (e.g., "what about exit load?") may use the last referenced scheme — but only within the same thread and only if confidence is high.
- Thread state stores: `thread_id`, `last_scheme_name`, `last_route`, `message_history` (last N turns only).

#### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/threads` | Create a new conversation thread |
| `GET` | `/threads/:id` | Fetch thread state and history |
| `POST` | `/threads/:id/messages` | Submit a question and receive an answer |
| `GET` | `/sources` | View the approved corpus and last crawl status |
| `POST` | `/ingest/run` | Trigger a source refresh for approved URLs |
| `GET` | `/eval/runs/:id` | Fetch evaluation run results |

#### Core Database Tables

- `threads` — thread ID, created at, last active
- `messages` — thread ID, question, answer, route, citation URL, source date
- `source_documents` — URL manifest with crawl metadata
- `source_chunks` — normalized chunk store with embeddings
- `scheme_fact_cards` — structured flat facts per scheme
- `retrieval_logs` — query, route, evidence chunk ID, citation URL
- `citations` — citation URL, domain, source date, used count
- `refusal_logs` — query, refusal reason, educational link returned
- `evaluation_runs` — test case set ID, pass/fail per compliance check

**Output:** Thread-safe backend with all endpoints and audit logging.

---

### Phase 8: Tiny Groww-Style UI

#### UI Design Reference

The interface should be **Groww-inspired and intentionally minimal** — clean, trustworthy, and focused on one task. No financial charts, return tables, or fund comparison widgets.

#### Required UI Elements

| Element | Detail |
|---|---|
| Welcome line | "Ask any factual question about SBI Mutual Fund schemes." |
| Example questions (3) | See below |
| Disclaimer note | `Facts-only. No investment advice.` — visible at all times |
| Input box | Single text input, autofocus |
| Answer card | 1–3 sentences, one clickable source link, last-updated footer |
| Refusal card | Polite refusal with one educational link |
| Thread switcher | New chat button to start an independent thread |

#### Example Questions (shown in UI)

1. What is the expense ratio of SBI Large Cap Fund?
2. What is the minimum SIP amount for SBI Flexicap Fund?
3. How can I download my capital gains report from the Smart Statement portal?

#### UI Behavior Rules

- Advisory queries show the refusal message in the same answer area — no separate page.
- Only one source link displayed per answer — never multiple links.
- Do not expose raw chunks, model reasoning, or retrieval scores.
- Do not show performance charts or return calculations.
- Source URL shown as a clearly labeled, single clickable link below the answer.
- `Last updated from sources: <date>` footer shown in every answer card.

**Output:** Deployed minimal chat UI.

---

### Phase 9: Evaluation, Refusal Testing, and Citation Validation

#### Test Buckets

| Bucket | Description |
|---|---|
| Supported factual queries | Expense ratio, exit load, min SIP, benchmark, riskometer, ELSS lock-in |
| Process queries | Statement download, capital gains, forms, NRI process |
| Performance queries | Check that only factsheet link is returned, no return computation |
| Advisory refusal | "Should I invest?", "Which is better?", "Is this good for me?" |
| Restricted-data refusal | Queries containing or requesting PAN, OTP, Aadhaar, account number |
| Wrong-scheme disambiguation | "SBI Bluechip Fund" → resolves to SBI Large Cap Fund |
| Missing-answer cases | Evidence not found or stale → no-answer policy fires |
| Multi-thread isolation | Scheme from Thread A does not leak into Thread B |
| Source freshness | Stale crawl detected and flagged |

#### Compliance Checks Per Answer

- [ ] Sentence count is 3 or fewer
- [ ] Exactly one link present in the answer
- [ ] Link domain is on the allowlist
- [ ] Footer is present
- [ ] Advisory prompt correctly refused
- [ ] Performance query returns only factsheet link — no computed value
- [ ] Restricted-data query refused with privacy warning
- [ ] Retrieved source scheme matches the scheme named in the answer
- [ ] No sensitive data echoed back in any response

#### Evaluation Metrics

| Metric | Description |
|---|---|
| Retrieval hit rate @5 | Fraction of queries where correct chunk is in top 5 |
| Wrong-scheme retrieval rate | Fraction of queries where wrong scheme chunk is returned |
| Refusal precision | Fraction of advisory queries correctly refused |
| Citation-validity rate | Fraction of answers with a valid allowlisted URL |
| Footer-compliance rate | Fraction of answers with the correct footer |
| Stale-source rate | Fraction of sources not refreshed within the refresh window |
| Avg response latency | End-to-end latency from query to formatted answer |

---

## Privacy and Safety

The architecture **must** enforce the following at both the API and UI layer:

- Do **not** collect, store, or process PAN numbers, Aadhaar numbers, account numbers, OTPs, email addresses, or phone numbers.
- Any query that contains or requests such information must be classified as `restricted_data_refusal` and refused immediately.
- The refusal must include a warning not to share sensitive personal or financial information with any chatbot.
- No user input that contains such data should enter the retrieval pipeline or be logged in plaintext.

**Refusal template for restricted-data queries:**

> Please do not share personal or financial information such as PAN, Aadhaar, account numbers, or OTPs with any chatbot. This assistant handles only factual mutual fund questions from official public sources.

---

## Facts-Only Rules

| Rule | Detail |
|---|---|
| No investment advice | Never recommend, suggest, or imply any investment action |
| No buy / sell / hold | Never indicate whether to invest, redeem, or hold any scheme |
| No "which fund is better" | Never compare two funds or rank them |
| No portfolio construction | Never suggest allocation percentages or portfolio strategies |
| No suitability advice | Never assess whether a fund is suitable for a user's goal or profile |
| No return calculations | Never compute CAGR, absolute return, or projected value |
| No rankings | Never rank or order schemes by any metric |

---

## Recommended Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React or Next.js — Groww-inspired minimal chat UI |
| Backend | Python FastAPI |
| HTML parser | BeautifulSoup / Playwright for JS-rendered pages |
| Structured DB | PostgreSQL |
| Vector Store | Chroma Cloud (Managed) |
| Embedding model | `bge-base-en-v1.5` (BAAI) — 768 dimensions (local) |
| Keyword search | BM25 (rank-bm25 Python library or Elasticsearch) |
| Reranker | Cross-encoder or reciprocal rank fusion |
| Scheduler | **GitHub Actions** — cron `45 3 * * *` (09:15 AM IST daily); `workflow_dispatch` for manual trigger |
| Scraping service | `requests` + `BeautifulSoup` for static HTML; `Playwright` (headless Chromium) for Angular SPA pages (`esoa`, `corporate`) |
| Observability | Retrieval logs, refusal logs, evaluation store in PostgreSQL |
| Build coordinator | Antigravity — workspace execution, artifact review, iterative development |

---

## Deliverables

| Deliverable | Format | Description |
|---|---|---|
| Working prototype | Live link or demo video | End-to-end assistant with UI, refusal, and citation |
| Source list | CSV or MD file | All 15–25 URLs used with domain, type, scheme tag, crawl status |
| README | Markdown | Setup steps, chosen product (Groww), chosen AMC (SBI MF), chosen schemes, known limits |
| Sample Q&A file | Markdown | 5–10 queries covering factual, refusal, process, and performance route types |
| Disclaimer snippet | Text | `Facts-only. No investment advice.` |

---

## Known Limitations

- Source formats on SBIMF website may change without notice; crawl failures will mark sources as `stale` and are retried up to 3 times before the daily run is marked as partially failed.
- Some scheme detail pages may render key facts via JavaScript, requiring a headless browser for extraction.
- Structured fact cards must be manually verified after each daily refresh until an automated validation pipeline is in place; the content-hash check reduces unnecessary re-verification on unchanged pages.
- The one-link policy may limit context in complex multi-part questions that span more than one official document.
- Ambiguous user phrasing (e.g., "Bluechip Fund") requires a scheme-name resolution step to avoid wrong-scheme retrieval.
- The NRI corner and corporate portal may have limited factual text accessible without login.

---

## Operational Rules

- Never collect PAN, Aadhaar, account numbers, OTPs, phone numbers, or email addresses.
- Never answer advisory, comparative, or portfolio-related queries.
- Never use third-party blogs, aggregators, or distributor site data as factual evidence.
- Never generate return calculations, NAV projections, or performance comparisons.
- For performance-related queries, return only the official SBI MF factsheet link.
- Log every answer with: `source_url`, `source_date`, `route`, `evidence_chunk_id`, `thread_id`.
- Reject any domain not on the allowlist at ingestion time — do not crawl or index it.

---

## Final Implementation View

The target system behaves as follows:

1. User submits a question in the Groww-inspired minimal UI.
2. Query classifier assigns one of 6 routes before any retrieval runs.
3. If advisory or restricted-data: refuse immediately with one official educational link.
4. If factual: hybrid retrieval (structured fact card lookup → BM25 → vector search → rerank) returns the best evidence chunk.
5. Deterministic citation selection picks exactly one official URL from the allowlisted priority order.
6. Answer composer fills the strict 3-sentence contract and appends source link and footer.
7. UI displays the answer card with the source link and `Last updated from sources: <date>` footer.
8. Every query, route, evidence chunk, and citation is logged for audit and evaluation.
9. **Daily 9:15 AM IST** — scheduler triggers the scraping service which re-crawls all 20 approved URLs in priority order, runs PII guard, computes content hashes (skipping unchanged pages), re-chunks updated pages, and flags stale or failed sources in the crawl log.

This architecture keeps the LLM narrowly scoped to language generation. Routing, source control, citation choice, privacy guards, and compliance checks are all deterministic — making the system safe, auditable, and maintainable as a facts-only mutual fund assistant aligned to the Groww product context and the SBI Mutual Fund official corpus.
