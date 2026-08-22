"""
Swiss Data Airlock — Core Algorithm
PII detection, tokenization, and detokenization.
"""

from .engine import AirlockEngine, MaskResult, DetectedEntity
from .tokenizer import TokenGenerator, anonymize, detokenize
from .detector import detect_entities, SwissIBANRecognizer, SwissAHVRecognizer
from .patterns import TOKEN_LABELS, SWISS_IBAN_PATTERNS, SWISS_AHV_PATTERNS

__all__ = [
    "AirlockEngine",
    "MaskResult",
    "DetectedEntity",
    "TokenGenerator",
    "anonymize",
    "detokenize",
    "detect_entities",
    "SwissIBANRecognizer",
    "SwissAHVRecognizer",
    "TOKEN_LABELS",
    "SWISS_IBAN_PATTERNS",
    "SWISS_AHV_PATTERNS",
]
