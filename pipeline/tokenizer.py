"""
pipeline/tokenizer.py
Tier-1 utility to provide consistent token counting across chunking and retrieval.
Uses tiktoken with 'cl100k_base' encoding (GPT-4 / text-embedding-3-small).
"""

import tiktoken
import logging

logger = logging.getLogger(__name__)

# Use cl100k_bases as it's the encoding for text-embedding-3-small
_ENCODING = "cl100k_base"

def get_token_count(text: str) -> int:
    """Return the number of tokens in a string."""
    try:
        encoding = tiktoken.get_encoding(_ENCODING)
        return len(encoding.encode(text))
    except Exception as e:
        logger.error("Token counting failed: %s", e)
        # Crude fallback if tiktoken fails: ~4 chars per token
        return len(text) // 4

def get_tokens(text: str) -> list[int]:
    """Return the list of tokens for a string."""
    encoding = tiktoken.get_encoding(_ENCODING)
    return encoding.encode(text)

def decode_tokens(tokens: list[int]) -> str:
    """Return the string for a list of tokens."""
    encoding = tiktoken.get_encoding(_ENCODING)
    return encoding.decode(tokens)
