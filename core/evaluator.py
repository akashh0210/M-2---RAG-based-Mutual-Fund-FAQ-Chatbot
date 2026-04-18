"""
core/evaluator.py
Phase 9 — QA: Evaluation, Refusal Testing, and Citation Validation

Automates the validation of RAG assistant responses against a golden dataset.
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Any

from core.engine import RAGEngine, EngineResult
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("core.evaluator")

# ── Configuration ─────────────────────────────────────────────────────────────

EVAL_SET_PATH = "data/eval_set.json"
EVAL_RESULTS_PATH = "data/eval_results.json"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
JUDGE_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

ALLOWED_DOMAINS = ["sbimf.com", "amfiindia.com", "mutualfundssahihai.com", "sebi.gov.in"]

# ── Judge Prompt ──────────────────────────────────────────────────────────────

JUDGE_PROMPT = """
You are an expert quality auditor for a Mutual Fund RAG assistant.
Your task is to grade the assistant's response based on the query and the provided evidence.

QUERY: {query}
EVIDENCE: {evidence}
RESPONSE: {response}

Grade on a scale of 1-5 for the following:
1. RELEVANCE: Does the answer directly address the user's question?
2. FAITHFULNESS: Is every fact in the response substantiated by the evidence? (Score 5 if it's a correct refusal).

Return JSON ONLY:
{{"relevance": 0, "faithfulness": 0, "reasoning": "..."}}
"""

# ── Evaluator Class ─────────────────────────────────────────────────────────────

class RAGEvaluator:
    def __init__(self):
        self.engine = RAGEngine()
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        
    def run_suite(self):
        """Execute the full evaluation suite."""
        if not os.path.exists(EVAL_SET_PATH):
            logger.error("Eval set not found at %s", EVAL_SET_PATH)
            return

        with open(EVAL_SET_PATH, "r") as f:
            test_cases = json.load(f)

        results = []
        logger.info("Starting evaluation of %d cases...", len(test_cases))

        for case in test_cases:
            logger.info("Testing Case %s: %s", case["id"], case["query"])
            
            start_time = time.time()
            engine_result: EngineResult = self.engine.process_query(case["query"])
            latency = time.time() - start_time
            
            # 1. Compliance Logic
            compliance = self._check_compliance(case, engine_result)
            
            # 2. Quality Logic (LLM Judge)
            quality = self._grade_quality(case, engine_result) if self.client else {"relevance": 0, "faithfulness": 0}

            result = {
                "id": case["id"],
                "query": case["query"],
                "category": case["category"],
                "intent": engine_result.intent.intent,
                "intent_correct": engine_result.intent.intent == case["expected_intent"],
                "response": engine_result.answer,
                "latency": latency,
                "compliance": compliance,
                "quality": quality
            }
            results.append(result)

        # Save Results
        with open(EVAL_RESULTS_PATH, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info("Evaluation complete. Results saved to %s", EVAL_RESULTS_PATH)
        return results

    def _check_compliance(self, case: dict, result: EngineResult) -> dict:
        """Check if the response follows the 'One-Link Contract' and other rules."""
        answer = result.answer or ""
        
        # Sentence Count
        sentences = [s for s in re.split(r'[.!?]+', answer) if s.strip()]
        sentence_count_ok = len(sentences) <= 3
        
        # Exactly One Link
        links = re.findall(r'https?://[^\s)\]]+', answer)
        link_count_ok = len(links) == 1
        
        # Domain Allowlist
        domain_ok = True
        if links:
            link = links[0]
            domain_ok = any(domain in link for domain in ALLOWED_DOMAINS)
            
        # Footer check
        footer_ok = "Last updated from sources" in answer
        
        # Refusal check
        refusal_ok = True
        if case["expected_refusal"]:
            refusal_ok = result.is_refused or "cannot recommend" in answer.lower() or "only factual" in answer.lower()

        return {
            "sentence_count": len(sentences),
            "sentence_count_ok": sentence_count_ok,
            "link_count": len(links),
            "link_count_ok": link_count_ok,
            "domain_ok": domain_ok,
            "footer_ok": footer_ok,
            "refusal_ok": refusal_ok,
            "all_passed": all([sentence_count_ok, link_count_ok, domain_ok, footer_ok, refusal_ok])
        }

    def _grade_quality(self, case: dict, result: EngineResult) -> dict:
        """Use an LLM Judge to score the response quality."""
        evidence = result.evidence.content if result.evidence else "No evidence provided (Refusal Case)."
        
        prompt = JUDGE_PROMPT.format(
            query=case["query"],
            evidence=evidence,
            response=result.answer
        )

        try:
            completion = self.client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            raw_grade = completion.choices[0].message.content.strip()
            # Extract JSON from potential triple backticks
            if "```json" in raw_grade:
                raw_grade = raw_grade.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_grade:
                raw_grade = raw_grade.split("```")[1].strip()
            
            return json.loads(raw_grade)
        except Exception as e:
            logger.error("Judge failed for %s: %s", case["id"], e)
            return {"relevance": 0, "faithfulness": 0, "reasoning": "Error"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    evaluator = RAGEvaluator()
    evaluator.run_suite()
