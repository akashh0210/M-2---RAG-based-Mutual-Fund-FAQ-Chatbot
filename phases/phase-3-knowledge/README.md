# Phase 3 — Structured Fact Cards and Chunk Indexing

**Status: 🔲 Not Started**
**Prerequisite:** Phase 2 complete (raw text files in `data/raw/`)

## What Will Be Built

- Full implementation of `pipeline/chunk.py` — per page-type splitting
- `pipeline/embed.py` — batch embedding via `text-embedding-3-small`
- `scheme_fact_cards` table — extracted exact values per scheme
- Vector index via pgvector (IVFFlat, 1536 dims)

## Architecture Reference

See [`docs/chunking-embedding-architecture.md`](../../docs/chunking-embedding-architecture.md)
