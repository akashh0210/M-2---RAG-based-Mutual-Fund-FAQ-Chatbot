# Phase 7 — Backend API and Multi-Thread Support

**Status: 🔲 Not Started**
**Prerequisite:** Phase 6 complete

## What Will Be Built

- FastAPI backend with thread model
- Endpoints: `/threads`, `/threads/:id`, `/threads/:id/messages`, `/sources`, `/ingest/run`
- Thread-safe state: `thread_id`, `last_scheme_name`, `last_route`, message history
- Audit logging: every query, route, evidence chunk, and citation logged
- `messages`, `threads`, `retrieval_logs`, `refusal_logs`, `citations` DB tables

## Architecture Reference

See Phase 7 section in [`docs/RAG-mutual-fund-faq-architecture.md`](../../docs/RAG-mutual-fund-faq-architecture.md)
