"""
main.py
Phase 7 — Backend API and Multi-Thread Support

FastAPI implementation to expose the RAG engine as a web service.
Supports thread-based memory and context.
"""

import uuid
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.engine import RAGEngine, EngineResult
from pipeline.models import (
    get_connection, 
    get_thread_history, 
    init_db
)

# ── Configuration ─────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(
    title="SBI Mutual Fund RAG Assistant API",
    description="Backend service for Phase 7 of the Mutual Fund FAQ Chatbot.",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine
engine = RAGEngine()

# Ensure DB is ready
conn = get_connection()
init_db(conn)
conn.close()

# ── Schema ──────────────────────────────────────────────────────────────────

class MessageRequest(BaseModel):
    query: str = Field(..., example="What is the exit load for SBI Bluechip Fund?")

class MessageResponse(BaseModel):
    answer: str
    intent: str
    scheme_name: Optional[str]
    source_url: Optional[str]
    thread_id: str
    is_refused: bool

class ThreadResponse(BaseModel):
    thread_id: str
    history: List[dict]

# ── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/threads", response_model=ThreadResponse)
async def create_thread():
    """Create a new conversation thread."""
    thread_id = str(uuid.uuid4())
    logger.info("Created new thread: %s", thread_id)
    return {"thread_id": thread_id, "history": []}


@app.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(thread_id: str):
    """Fetch history for a specific thread."""
    conn = get_connection()
    history = get_thread_history(conn, thread_id)
    conn.close()
    
    # history is returned as list of dicts: role, content, metadata
    return {"thread_id": thread_id, "history": history}


@app.post("/threads/{thread_id}/messages", response_model=MessageResponse)
async def post_message(thread_id: str, request: MessageRequest):
    """Submit a question to a thread and get an answer."""
    try:
        result: EngineResult = engine.process_query(request.query, thread_id=thread_id)
        
        return MessageResponse(
            answer=result.answer or "No response generated.",
            intent=result.intent.intent,
            scheme_name=result.intent.scheme_name,
            source_url=result.evidence.metadata.get("source_url") if result.evidence else None,
            thread_id=thread_id,
            is_refused=result.is_refused
        )
    except Exception as e:
        logger.error("Error processing message in thread %s: %s", thread_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sources")
async def list_sources():
    """List the 20 approved URLs and their last crawl status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT scheme_name, official_url, status, last_crawled_at FROM source_documents")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
