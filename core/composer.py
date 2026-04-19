"""
core/composer.py
Phase 6 — Answer Formatter and One-Link Contract

Synthesizes retrieved evidence into a 3-sentence, facts-only response.
Uses Groq (Llama-3-70b) for high-speed, accurate inference.
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

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

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
Refuse politely and clearly.
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
            logger.error("LLM composition failed: %s", err_msg, exc_info=True)
            # Fallback to mock mode instead of showing a scary connection error
            return self._mock_compose(query, evidence, is_refusal, debug_error=err_msg)

    def _generate_answer(self, query: str, evidence: RetrievalResult) -> str:
        """Generate a factual answer from evidence with retry logic."""
        
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
                # Format date to YYYY-MM-DD
                dt = datetime.fromisoformat(source_date.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%Y-%m-%d")
            except:
                formatted_date = str(source_date)[:10]
        else:
            formatted_date = datetime.now().strftime("%Y-%m-%d")

        # Context Truncation: Groq has tight TPM limits.
        # 12,000 chars is roughly 3,000 tokens, which fits in most tiers Safely.
        safe_content = evidence.content
        if len(safe_content) > 12000:
            logger.info("Truncating evidence content from %d to 12000 chars", len(safe_content))
            safe_content = safe_content[:12000] + "\n[... Content truncated for brevity ...]"

        prompt = f"Evidence:\n{safe_content}\n\nURL: {source_url}\nDate: {formatted_date}\n\nQuestion: {query}"

        return self._call_groq_with_retry(
            messages=[
                {"role": "system", "content": ANSWER_COMPOSER_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=512
        )

    def _generate_refusal(self, query: str, refusal_template: Optional[str]) -> str:
        """Generate a polite refusal with retry logic."""
        
        context = f"Question: {query}"
        if refusal_template:
            context += f"\n\nBaseline Refusal Template (follow this logic): {refusal_template}"

        return self._call_groq_with_retry(
            messages=[
                {"role": "system", "content": REFUSAL_ROUTER_PROMPT},
                {"role": "user", "content": context}
            ],
            temperature=0.2,
            max_tokens=256
        )

    def _call_groq_with_retry(self, messages: List[dict], temperature: float, max_tokens: int, retries: int = 3) -> str:
        """Helper to call Groq with exponential backoff for rate limits."""
        for i in range(retries):
            try:
                completion = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                err_str = str(e).lower()
                if ("rate_limit" in err_str or "429" in err_str) and i < retries - 1:
                    wait_time = (2 ** i) + random.random()
                    logger.warning("Groq Rate Limit hit. Retrying in %.2f seconds... (Attempt %d/%d)", wait_time, i+1, retries)
                    time.sleep(wait_time)
                    continue
                # If it's not a rate limit or we're out of retries, raise it
                raise e

    def _mock_compose(self, query: str, evidence: Optional[RetrievalResult], is_refusal: bool, debug_error: Optional[str] = None) -> str:
        """Fallback mock if API key is missing or service is down."""
        debug_tag = f"\n\n[System Diagnostic: {debug_error}]" if debug_error else ""
        
        if is_refusal:
            return f"This assistant provides only factual information from official mutual fund sources. For investor education, please refer to: https://www.mutualfundssahihai.com/en/about-us{debug_tag}"
        
        if not evidence:
            return f"I couldn't verify that from current official sources. Please check the official AMC website.{debug_tag}"
            
        # Try multiple keys for source URL
        url = (
            evidence.metadata.get("source_url") or 
            evidence.metadata.get("official_url") or 
            evidence.metadata.get("url") or 
            "official SBI Mutual Fund sources"
        )
        
        # Return a larger, more useful snippet in mock mode
        snippet = evidence.content[:400].strip()
        if len(evidence.content) > 400:
            snippet += "..."

        return f"Based on official documents: {snippet}\n\nSource: {url}\nLast updated: {datetime.now().strftime('%Y-%m-%d')}{debug_tag}"

# Testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    composer = AnswerComposer()
    
    # Example mock test
    # res = RetrievalResult(source="fact_card", content="The exit load is 1% if redeemed within 1 year.", metadata={"source_url": "https://example.com"})
    # print(composer.compose("What is the exit load?", res))
