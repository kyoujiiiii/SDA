"""
PII detection using Microsoft Presidio + custom Swiss regex patterns.
"""

from typing import List

from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider

from .patterns import TOKEN_LABELS, SWISS_IBAN_PATTERNS, SWISS_AHV_PATTERNS


class SwissIBANRecognizer(PatternRecognizer):
    """Custom recognizer for Swiss IBAN (CH + 2 check digits + 17 alphanumeric)."""

    def __init__(self):
        super().__init__(
            supported_entity="IBAN",
            name="Swiss IBAN Recognizer",
            patterns=SWISS_IBAN_PATTERNS,
            supported_language="en",
        )


class SwissAHVRecognizer(PatternRecognizer):
    """Custom recognizer for Swiss AHV/AVS (756.xxxx.xxxx.xx)."""

    def __init__(self):
        super().__init__(
            supported_entity="AHV_NUMBER",
            name="Swiss AHV/AVS Recognizer",
            patterns=SWISS_AHV_PATTERNS,
            supported_language="en",
        )


_analyzer = None


def _get_analyzer() -> AnalyzerEngine:
    """Lazy-init Presidio analyzer with spaCy + Swiss recognizers."""
    global _analyzer
    if _analyzer is not None:
        return _analyzer

    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
    }
    provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
    nlp_engine = provider.create_engine()

    _analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
    _analyzer.registry.add_recognizer(SwissIBANRecognizer())
    _analyzer.registry.add_recognizer(SwissAHVRecognizer())

    return _analyzer


def detect_entities(text: str, language: str = "en") -> list:
    """
    Detect PII entities in text using Presidio + Swiss patterns.

    Returns:
        List of RecognizerResult objects (with .start, .end, .entity_type, .score)
    """
    analyzer = _get_analyzer()
    entities = list(TOKEN_LABELS.keys())
    return analyzer.analyze(text=text, entities=entities, language=language)
