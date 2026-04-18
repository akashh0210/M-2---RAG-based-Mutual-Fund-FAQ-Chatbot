# Deployment Architecture Plan

This document outlines the deployment strategy for the Mutual Funds AI Application, dividing it into three environments for optimal stability and memory management.

## 1. Data Ingestion Scheduler (GitHub Actions)

*   **Platform:** GitHub Actions
*   **Trigger:** Scheduled Cron Job (Daily)
*   **Responsibilities:** Scraping, Embedding, and Syncing to Chroma Cloud.
*   **Required Provider Secrets in GitHub:**
    *   `GROQ_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE`, `CHROMA_API_KEY`

## 2. RAG Back-End & API Engine (Hugging Face Spaces)

We use Hugging Face Spaces because it provides **16GB RAM** for free, preventing the memory crashes seen on other platforms.

*   **Platform:** Hugging Face Spaces (Docker SDK)
*   **RAM:** 16GB (Free Tier)
*   **Architecture:** Dockerized FastAPI
*   **Sync Logic:** GitHub code is mirrored to HF via a GitHub Action.
*   **Required Secret Variables in Hugging Face:**
    *   Go to **Settings > Variables and secrets** in your Space.
    *   Add: `GROQ_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE`, `CHROMA_API_KEY`.
*   **URL:** `https://<hf-username>-<space-name>.hf.space`

## 3. Front-End Web Client (Vercel)

*   **Platform:** Vercel
*   **Framework:** Next.js
*   **Root Directory:** `frontend/`
*   **Required Environment Variable:**
    *   `NEXT_PUBLIC_API_URL`: Your Hugging Face Space URL.

---

### Sync Instructions: GitHub to Hugging Face
Because Hugging Face uses its own internal Git, we use the `hf-sync.yml` workflow to keep them in sync. 
1. Create a "Write" token at https://huggingface.co/settings/tokens.
2. Add it as `HF_TOKEN` in your GitHub Repo Secrets.
