"""
core/composer.py
Phase 6 — Answer Formatter and One-Link Contract

Synthesizes retrieved evidence into a 3-sentence, facts-only response.
Uses Groq (Llama-3-70b) for high-speed, accurate inference.
"""

import logging
import os
import re
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
            logger.error("LLM composition failed: %s", e)
            # Fallback to mock mode instead of showing a scary connection error
            return self._mock_compose(query, evidence, is_refusal)

    def _generate_answer(self, query: str, evidence: RetrievalResult) -> str:
        """Generate a factual answer from evidence."""
        
        source_url = evidence.metadata.get("source_url") or evidence.metadata.get("official_url", "N/A")
        
        # Try to extract date from metadata
        source_date = evidence.metadata.get("crawled_at") or evidence.metadata.get("last_updated_at")
        if source_date:
            try:
                # Format date to YYYY-MM-DD
                dt = datetime.fromisoformat(source_date.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%Y-%m-%d")
            except:
                formatted_date = source_date[:10]
        else:
            formatted_date = datetime.now().strftime("%Y-%m-%d")

        prompt = f"Evidence:\n{evidence.content}\n\nURL: {source_url}\nDate: {formatted_date}\n\nQuestion: {query}"

        completion = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": ANSWER_COMPOSER_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Deterministic for facts
            max_tokens=256
        )

        answer = completion.choices[0].message.content.strip()
        
        # Final safety check: Ensure it has the link and footer
        if "Source:" not in answer and source_url != "N/A":
            answer += f"\n\nSource: {source_url}"
        
        if "Last updated" not in answer:
            answer += f"\nLast updated from sources: {formatted_date}"

        return answer

    def _generate_refusal(self, query: str, refusal_template: Optional[str] = None) -> str:
        """Generate a polite refusal for advisory/restricted queries."""
        
        context = f"Question: {query}"
        if refusal_template:
            context += f"\n\nBaseline Refusal Template (follow this logic): {refusal_template}"

        completion = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": REFUSAL_ROUTER_PROMPT},
                {"role": "user", "content": context}
            ],
            temperature=0.2,
            max_tokens=256
        )
        return completion.choices[0].message.content.strip()

    def _mock_compose(self, query: str, evidence: Optional[RetrievalResult], is_refusal: bool) -> str:
        """Fallback mock if API key is missing."""
        if is_refusal:
            return "This assistant provides only factual information from official mutual fund sources. For investor education, please refer to: https://www.mutualfundssahihai.com/en/about-us"
        
        if not evidence:
            return "I couldn't verify that from current official sources."
            
        return f"{evidence.content[:200]}...\n\nSource: {evidence.metadata.get('source_url', 'N/A')}\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}"

# Testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    composer = AnswerComposer()
    
    # Example mock test
    # res = RetrievalResult(source="fact_card", content="The exit load is 1% if redeemed within 1 year.", metadata={"source_url": "https://example.com"})
    # print(composer.compose("What is the exit load?", res))
