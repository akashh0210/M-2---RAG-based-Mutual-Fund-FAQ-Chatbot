"""
core/composer.py
Phase 6 — Answer Formatter and One-Link Contract

Synthesizes retrieved evidence into a 3-sentence, facts-only response.
Uses Groq with dual-model fallback for reliability.
"""

import logging
import os
import re
import time
import random
from typing import Optional, List
from datetime import datetime

from groq import Groq
from dotenv import load_dotenv

from core.retriever import RetrievalResult

load_dotenv()

logger = logging.getLogger("core.composer")

# ── Configuration ─────────────────────────────────────────────────────────────

GROQ_PRIMARY_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_FALLBACK_MODEL = os.environ.get("GROQ_FALLBACK_MODEL", "gemma2-9b-it")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Token budget: Evidence is truncated to ~1000 tokens (4000 chars).
# System prompt ~150 tokens + query ~50 tokens + response 256 tokens ≈ 1,500 tokens/query.
# With 100k daily limit, this supports ~66 queries/day on the free tier.
MAX_EVIDENCE_CHARS = 4000
MAX_RESPONSE_TOKENS = 256

# ── System Prompts ────────────────────────────────────────────────────────────

ANSWER_COMPOSER_PROMPT = """
You are a facts-only mutual fund FAQ assistant for SBI Mutual Fund schemes.
Answer only from the supplied official evidence text.
Do not provide advice, recommendations, comparisons, opinions, or suitability guidance.
Do not compute or compare returns or performance.
Use at most 3 sentences.
Include exactly one source link from the evidence.
Always end with: Last updated from sources: <date>
If evidence is insufficient or ambiguous, say you could not verify it from current official sources.
"""

REFUSAL_ROUTER_PROMPT = """
The user has asked an advisory, comparative, or restricted question.
Refuse politely and clearly in 2 sentences.
State that this assistant provides only factual information from official mutual fund sources.
Provide exactly one educational link from SEBI or Mutual Funds Sahi Hai.
Do not provide any investment guidance or fund comparison.
"""

# ── Service Class ─────────────────────────────────────────────────────────────

class AnswerComposer:
    def __init__(self):
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not found in environment. Composer will be in mock mode.")
            self.client = None
        else:
            self.client = Groq(api_key=GROQ_API_KEY)

    def compose(self, query: str, evidence: Optional[RetrievalResult], is_refusal: bool = False, refusal_template: Optional[str] = None) -> str:
        """Compose the final response using the LLM."""
        
        if not self.client:
            return self._mock_compose(query, evidence, is_refusal)

        try:
            if is_refusal:
                return self._generate_refusal(query, refusal_template)
            
            if not evidence:
                return "I couldn't verify that from the current official sources. Please check the official scheme document or AMC support page."

            return self._generate_answer(query, evidence)

        except Exception as e:
            err_msg = str(e)
            logger.error("LLM composition failed (all models exhausted): %s", err_msg, exc_info=True)
            return self._mock_compose(query, evidence, is_refusal)

    def _generate_answer(self, query: str, evidence: RetrievalResult) -> str:
        """Generate a factual answer from evidence."""
        
        # Try multiple keys for source URL
        source_url = (
            evidence.metadata.get("source_url") or 
            evidence.metadata.get("official_url") or 
            evidence.metadata.get("url") or 
            "N/A"
        )
        
        # Try to extract date from metadata
        source_date = evidence.metadata.get("crawled_at") or evidence.metadata.get("last_updated_at")
        if source_date:
            try:
                dt = datetime.fromisoformat(source_date.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%Y-%m-%d")
            except Exception:
                formatted_date = str(source_date)[:10]
        else:
            formatted_date = datetime.now().strftime("%Y-%m-%d")

        # Aggressive Context Truncation to conserve daily token budget.
        safe_content = evidence.content[:MAX_EVIDENCE_CHARS].strip()
        if len(evidence.content) > MAX_EVIDENCE_CHARS:
            logger.info("Truncating evidence from %d to %d chars", len(evidence.content), MAX_EVIDENCE_CHARS)

        prompt = f"Evidence:\n{safe_content}\n\nURL: {source_url}\nDate: {formatted_date}\n\nQuestion: {query}"

        return self._call_groq_with_fallback(
            messages=[
                {"role": "system", "content": ANSWER_COMPOSER_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=MAX_RESPONSE_TOKENS
        )

    def _generate_refusal(self, query: str, refusal_template: Optional[str]) -> str:
        """Generate a polite refusal."""
        
        context = f"Question: {query}"
        if refusal_template:
            context += f"\n\nBaseline Refusal Template (follow this logic): {refusal_template}"

        return self._call_groq_with_fallback(
            messages=[
                {"role": "system", "content": REFUSAL_ROUTER_PROMPT},
                {"role": "user", "content": context}
            ],
            temperature=0.2,
            max_tokens=128
        )

    def _call_groq_with_fallback(self, messages: List[dict], temperature: float, max_tokens: int) -> str:
        """Try primary model, then fallback model. Each has its own daily token budget."""
        
        models_to_try = [GROQ_PRIMARY_MODEL, GROQ_FALLBACK_MODEL]
        last_error = None
        
        for model in models_to_try:
            try:
                result = self._call_groq(model, messages, temperature, max_tokens)
                return result
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if "rate_limit" in err_str or "429" in err_str or "tokens" in err_str:
                    logger.warning("Model %s rate-limited, trying fallback...", model)
                    continue
                elif "decommissioned" in err_str or "not found" in err_str:
                    logger.warning("Model %s unavailable, trying fallback...", model)
                    continue
                else:
                    # Non-recoverable error (auth, server, etc.)
                    raise e
        
        # All models failed
        raise last_error

    def _call_groq(self, model: str, messages: List[dict], temperature: float, max_tokens: int) -> str:
        """Single Groq API call with one retry for transient errors."""
        for attempt in range(2):
            try:
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                err_str = str(e).lower()
                # Only retry on per-minute rate limits (not daily TPD limits)
                if "per minute" in err_str and attempt == 0:
                    wait_time = 2 + random.random()
                    logger.warning("RPM limit on %s, retrying in %.1fs...", model, wait_time)
                    time.sleep(wait_time)
                    continue
                raise e

    def _mock_compose(self, query: str, evidence: Optional[RetrievalResult], is_refusal: bool) -> str:
        """Fallback mock if API key is missing or all models are exhausted."""
        if is_refusal:
            return "This assistant provides only factual information from official mutual fund sources. For investor education, please refer to: https://www.mutualfundssahihai.com/en/about-us"
        
        if not evidence:
            return "I couldn't verify that from current official sources. Please check the official AMC website."
            
        # Try multiple keys for source URL
        url = (
            evidence.metadata.get("source_url") or 
            evidence.metadata.get("official_url") or 
            evidence.metadata.get("url") or 
            "official SBI Mutual Fund sources"
        )
        
        snippet = evidence.content[:400].strip()
        if len(evidence.content) > 400:
            snippet += "..."

        return f"Based on official documents: {snippet}\n\nSource: {url}\nLast updated: {datetime.now().strftime('%Y-%m-%d')}"

# Testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    composer = AnswerComposer()
    
    # Example mock test
    # res = RetrievalResult(source="fact_card", content="The exit load is 1% if redeemed within 1 year.", metadata={"source_url": "https://example.com"})
    # print(composer.compose("What is the exit load?", res))
