# Phase 5 — Hybrid Retrieval and Citation Selector

**Status: 🔲 Not Started**
**Prerequisite:** Phase 3 + Phase 4 complete

## What Will Be Built

- Hybrid retrieval pipeline: BM25 keyword search + pgvector semantic search
- Metadata filters: `amc_name`, `scheme_name`, `document_type`
- Reranking: reciprocal rank fusion (RRF)
- Deterministic citation selector (priority: factsheet URL > scheme page > service page > SEBI/AMFI)

## Architecture Reference

See Phase 5 section in [`docs/RAG-mutual-fund-faq-architecture.md`](../../docs/RAG-mutual-fund-faq-architecture.md)
