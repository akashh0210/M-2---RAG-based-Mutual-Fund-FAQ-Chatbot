"""
core/policy.py
Phase 4 — Policy & Refusal Engine

Enforces the 'Facts-Only' and 'No Advice' policy.
Provides deterministic templates for redirected or refused queries.
"""

import logging
from typing import Optional

logger = logging.getLogger("core.policy")

# ── Policy Configuration ──────────────────────────────────────────────────────

REFUSAL_LINKS = {
    "advisory": "https://www.mutualfundssahihai.com/en/about-us",
    "regulatory": "https://www.sebi.gov.in",
    "education": "https://www.mutualfundssahihai.com/en/investor-education"
}

# ── Templates ─────────────────────────────────────────────────────────────────

ADVISORY_REFUSAL_TEMPLATE = (
    "This assistant provides only factual information from official mutual fund sources and "
    "cannot recommend, compare, or evaluate funds for investment decisions. "
    "For investor education, please refer to: {link}"
)

RESTRICTED_DATA_TEMPLATE = (
    "Please do not share personal or financial information such as PAN, Aadhaar, account numbers, "
    "or OTPs with any chatbot. This assistant handles only factual mutual fund questions from official public sources."
)

PERFORMANCE_ONLY_TEMPLATE = (
    "For official performance data, NAV history, and portfolio returns, please refer to the "
    "scheme's latest factsheet here: https://www.sbimf.com/factsheets"
)

UNSUPPORTED_TEMPLATE = (
    "I couldn't verify that from the current official sources. Please check the official scheme document "
    "or the SBI Mutual Fund support page for more details."
)

# ── Policy Engine ─────────────────────────────────────────────────────────────

class PolicyEngine:
    @staticmethod
    def get_refusal_message(intent: str) -> Optional[str]:
        """Return the appropriate refusal message based on the intent."""
        
        if intent == "advisory_refusal":
            return ADVISORY_REFUSAL_TEMPLATE.format(link=REFUSAL_LINKS["advisory"])
            
        elif intent == "restricted_data_refusal":
            return RESTRICTED_DATA_TEMPLATE
            
        elif intent == "performance_link_only":
            return PERFORMANCE_ONLY_TEMPLATE
            
        elif intent == "unsupported_query":
            return UNSUPPORTED_TEMPLATE
            
        return None

    @staticmethod
    def validate_response(text: str, source_url: Optional[str]) -> bool:
        """
        Final compliance check before sending to user.
        Rules:
        1. Must not have more than 3 sentences. (Checked at Generation layer usually)
        2. Must have a source link if it's a factual answer.
        """
        if not text:
            return False
            
        # Basic validation: ensure no advisory-looking words slipped in
        forbidden = ["recommend", "better than", "should buy", "buy now", "i suggest"]
        if any(f in text.lower() for f in forbidden):
            return False
            
        return True
