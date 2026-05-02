"""
pipeline/pii_guard.py
PII (Personally Identifiable Information) guard for the RAG ingestion pipeline.

Scans extracted text for sensitive patterns and redacts them.
Applied TWICE: (1) at page level before chunking, (2) at chunk level after chunking.

Patterns covered per architecture spec:
  - PAN (Indian Permanent Account Number)
  - Aadhaar number
  - Email address
  - Indian mobile phone number
  - OTP / PIN (contextual — only flagged when near trigger words)

Returns:
  - redacted_text (str): text with PII tokens replaced by [REDACTED]
  - pii_found (bool): True if any PII was detected
  - alerts (list[str]): list of PII type names found
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── PII Regex Patterns ────────────────────────────────────────────────────────

_PAN_PATTERN = re.compile(
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
)

_AADHAAR_PATTERN = re.compile(
    r"\b\d{4}\s?\d{4}\s?\d{4}\b"
)

_EMAIL_PATTERN = re.compile(
    r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b"
)

_PHONE_PATTERN = re.compile(
    r"(?<!\d)(\+91[-\s]?)?[6-9]\d{9}(?!\d)"
)

# OTP/PIN — only flag if near a trigger word (contextual)
_OTP_TRIGGER = re.compile(
    r"\b(otp|one[\s-]time[\s-]password|pin|passcode|verification\s+code)\b",
    re.IGNORECASE,
)
_OTP_DIGIT_SEQUENCE = re.compile(r"\b\d{4,8}\b")

# ── Scraping-safe email allowlist ─────────────────────────────────────────────
# Known AMC contact emails that appear legitimately in page content
_ALLOWLISTED_EMAILS = {
    "customer.delight@sbimf.com",
    "investor@sbimf.com",
}


def _is_allowlisted_email(match: re.Match) -> bool:
    return match.group(0).lower() in _ALLOWLISTED_EMAILS


def scan_and_redact(text: str) -> tuple[str, bool, list[str]]:
    """
    Scan text for PII and redact all occurrences.

    Args:
        text: Raw extracted page or chunk text.

    Returns:
        Tuple of (redacted_text, pii_found, alerts)
        - redacted_text: text with PII replaced by [REDACTED]
        - pii_found: True if any PII was detected
        - alerts: list of PII type labels found
    """
    alerts: list[str] = []
    original_text = text
    redacted_text = text

    # 1. PAN
    if _PAN_PATTERN.search(redacted_text):
        redacted_text = _PAN_PATTERN.sub("[REDACTED-PAN]", redacted_text)
        alerts.append("PAN")

    # 2. Aadhaar — only flag 12-digit sequences not preceded/followed by more digits
    if _AADHAAR_PATTERN.search(redacted_text):
        redacted_text = _AADHAAR_PATTERN.sub("[REDACTED-AADHAAR]", redacted_text)
        alerts.append("AADHAAR")

    # 3. Email — skip allowlisted AMC contact emails
    for match in list(_EMAIL_PATTERN.finditer(redacted_text)):
        if not _is_allowlisted_email(match):
            alerts.append("EMAIL")
            redacted_text = redacted_text.replace(match.group(0), "[REDACTED-EMAIL]", 1)

    # 4. Phone
    if _PHONE_PATTERN.search(redacted_text):
        redacted_text = _PHONE_PATTERN.sub("[REDACTED-PHONE]", redacted_text)
        alerts.append("PHONE")

    # 5. OTP / PIN (contextual)
    # Only flag if a digit sequence (4-8 digits) is near a trigger word
    # Implementation: Find all triggers, then scan for nearby digit sequences.
    for trigger_match in _OTP_TRIGGER.finditer(redacted_text):
        trigger_pos = trigger_match.start()
        # Look for digit sequences within 50 chars before or after the trigger
        window_start = max(0, trigger_pos - 50)
        window_end = min(len(redacted_text), trigger_pos + 50)
        window = redacted_text[window_start:window_end]
        
        for digit_match in _OTP_DIGIT_SEQUENCE.finditer(window):
            val = digit_match.group(0)
            # Replace ONLY the specific occurrence near the trigger word
            abs_pos = window_start + digit_match.start()
            redacted_text = (
                redacted_text[:abs_pos]
                + "[REDACTED-OTP]"
                + redacted_text[abs_pos + len(val):]
            )
            alerts.append("OTP")

    pii_found = len(alerts) > 0

    if pii_found:
        logger.warning(
            "PII detected and redacted | types=%s | sample=%r",
            alerts,
            original_text[:80],
        )

    return redacted_text, pii_found, list(set(alerts))  # deduplicate alert types
