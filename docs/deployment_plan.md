# Deployment Architecture Plan

This document outlines the deployment strategy for the Mutual Funds AI Application, dividing the system into three distinct hosting environments for optimal performance, cost, and maintainability.

## 1. Data Ingestion Scheduler (GitHub Actions)

The RAG Data Pipeline requires a periodic scheduler to scrape the SBI MF knowledge base, generate embeddings, and sync them to ChromaDB. 

*   **Platform:** GitHub Actions
*   **Trigger:** Scheduled Cron Job (e.g., daily at midnight `0 0 * * *`)
*   **Workflow File:** `.github/workflows/daily-corpus-refresh.yml`
*   **Responsibilities:**
    *   Initialize Python environment.
    *   Run `python -m pipeline.run_pipeline`.
    *   Sync processed chunks and embeddings directly to the remote Chroma Cloud database.
*   **Required Provider Secrets in GitHub:**
    *   `GROQ_API_KEY`
    *   `CHROMA_TENANT`
    *   `CHROMA_DATABASE`
    *   `CHROMA_API_KEY`

## 2. RAG Back-End & API Engine (Render)

The FastAPI server acts as the core orchestration layer.

*   **Platform:** Render (Web Service)
*   **Runtime:** Python 3.11.9 (Locked via `PYTHON_VERSION` to avoid build failures)
*   **Model:** `all-MiniLM-L6-v2` (Optimized for 512MB RAM)
*   **Build Command:** `pip install -r requirements.txt`
*   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
*   **State Management:**
    *   Render ephemeral disks will wipe local SQLite data (`data/rag.db`) upon restart.
    *   **Action Required:** If you rely on `rag.db` for the "Recently Ingested" list in the Right Sidebar, you must attach a **Render Persistent Disk** mapped to `/app/data` to ensure the ingestion timestamps survive deployments and restarts.
*   **Required Environment Variables in Render:**
    *   `GROQ_API_KEY`
    *   `CHROMA_TENANT`
    *   `CHROMA_DATABASE`
    *   `CHROMA_API_KEY`

## 3. Front-End Web Client (Vercel)

The Next.js 14 application providing the Groww-inspired 3-column UI.

*   **Platform:** Vercel
*   **Framework:** Next.js
*   **Root Directory:** `frontend/`
*   **Build Command:** `npm run build`
*   **Responsibilities:**
    *   Serving the static landing page and interactive chat canvas.
    *   Managing local thread history via browser `localStorage`.
*   **Source Code Changes Required Before Deploy:**
    *   Update `frontend/src/lib/api.ts` to replace the hardcoded `http://localhost:8000` with the actual Render deployment URL (e.g., `https://mutual-funds-api.onrender.com`). It is recommended to use `process.env.NEXT_PUBLIC_API_URL`.
*   **Required Environment Variables in Vercel:**
    *   `NEXT_PUBLIC_API_URL=https://<your-render-url>.onrender.com`
