"""Tests for core.engine — AirlockEngine facade."""

import pytest

from core.engine import AirlockEngine, MaskResult, DetectedEntity


class TestAirlockEngine:
    @pytest.fixture
    def engine(self):
        return AirlockEngine()

    def test_mask_returns_mask_result(self, engine):
        result = engine.mask("Contact Hans Peter at hans@example.com")
        assert isinstance(result, MaskResult)
        assert isinstance(result.masked_text, str)
        assert isinstance(result.mapping, dict)
        assert isinstance(result.entities, list)

    def test_mask_replaces_pii(self, engine):
        result = engine.mask("Email hans@example.com")
        assert "hans@example.com" not in result.masked_text
        assert len(result.mapping) > 0

    def test_unmask_restores_original(self, engine):
        original = "Contract for Hans Peter, IBAN CH9300762011623852957"
        masked_result = engine.mask(original)
        restored = engine.unmask(masked_result.masked_text, masked_result.mapping)
        assert restored == original

    def test_mask_clean_text_unchanged(self, engine):
        text = "No PII here"
        result = engine.mask(text)
        assert result.masked_text == text
        assert len(result.entities) == 0

    def test_mask_result_entities_have_expected_fields(self, engine):
        result = engine.mask("hans@example.com")
        if result.entities:
            e = result.entities[0]
            assert isinstance(e, DetectedEntity)
            assert hasattr(e, "entity_type")
            assert hasattr(e, "start")
            assert hasattr(e, "end")
            assert hasattr(e, "original_value")
            assert hasattr(e, "token")
            assert hasattr(e, "score")

    def test_multiple_masks_same_session(self, engine):
        r1 = engine.mask("Hans Peter")
        r2 = engine.mask("Hans Peter")
        # Tokens should reset per call (generator is reset in anonymize)
        assert r1.mapping != {} or r2.mapping != {}
