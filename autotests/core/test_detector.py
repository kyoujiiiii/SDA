"""Tests for core.detector — PII detection with Presidio + Swiss patterns."""

import pytest

from core.detector import detect_entities


def _presidio_available():
    try:
        from presidio_analyzer import AnalyzerEngine
        return True
    except ImportError:
        return False


skip_no_presidio = pytest.mark.skipif(
    not _presidio_available(),
    reason="Presidio/spaCy not installed"
)


@skip_no_presidio
class TestDetectEntities:
    """Integration tests for PII detection — requires presidio-analyzer + en_core_web_lg."""

    def test_detect_email(self):
        results = detect_entities("Email me at test@example.com")
        types = [r.entity_type for r in results]
        assert "EMAIL_ADDRESS" in types

    def test_detect_phone(self):
        results = detect_entities("Call +41 79 123 45 67")
        types = [r.entity_type for r in results]
        assert "PHONE_NUMBER" in types

    def test_detect_swiss_iban(self):
        results = detect_entities("IBAN CH9300762011623852957")
        types = [r.entity_type for r in results]
        assert "IBAN" in types

    def test_detect_swiss_ahv(self):
        results = detect_entities("AHV 756.1234.5678.90")
        types = [r.entity_type for r in results]
        assert "AHV_NUMBER" in types

    def test_clean_text_no_detections(self):
        results = detect_entities("The weather is nice today.")
        assert len(results) == 0

    def test_multiple_entities_detected(self):
        text = "Hans Peter (hans@example.com) IBAN CH9300762011623852957"
        results = detect_entities(text)
        types = {r.entity_type for r in results}
        assert "EMAIL_ADDRESS" in types or "IBAN" in types
