"""Tests for core.tokenizer — TokenGenerator, anonymize, detokenize."""

import pytest

from core.tokenizer import TokenGenerator, anonymize, detokenize


class TestTokenGenerator:
    def test_sequential_tokens(self):
        gen = TokenGenerator()
        assert gen.next_token("PERSON") == "[PERSON_1]"
        assert gen.next_token("PERSON") == "[PERSON_2]"
        assert gen.next_token("IBAN") == "[IBAN_1]"

    def test_reset_clears_counters(self):
        gen = TokenGenerator()
        gen.next_token("PERSON")
        gen.next_token("PERSON")
        gen.reset()
        assert gen.next_token("PERSON") == "[PERSON_1]"

    def test_unknown_entity_uses_raw_label(self):
        gen = TokenGenerator()
        token = gen.next_token("CUSTOM_TYPE")
        assert token == "[CUSTOM_TYPE_1]"


class FakeEntity:
    """Minimal mock for RecognizerResult."""
    def __init__(self, start, end, entity_type, score=0.9):
        self.start = start
        self.end = end
        self.entity_type = entity_type
        self.score = score


class TestAnonymize:
    def test_single_entity(self):
        text = "Hello Hans Peter!"
        entities = [FakeEntity(6, 17, "PERSON")]
        gen = TokenGenerator()
        masked, mapping, detected = anonymize(text, entities, gen)

        assert "[PERSON_1]" in masked
        assert "Hans Peter" not in masked
        assert mapping["[PERSON_1]"] == "Hans Peter"
        assert len(detected) == 1

    def test_multiple_entities_sorted_by_position(self):
        text = "Email hans@example.com and name Hans Peter"
        entities = [
            FakeEntity(25, 36, "PERSON"),
            FakeEntity(6, 22, "EMAIL_ADDRESS"),
        ]
        gen = TokenGenerator()
        masked, mapping, detected = anonymize(text, entities, gen)

        # Both replaced
        assert "hans@example.com" not in masked
        assert "Hans Peter" not in masked
        assert len(mapping) == 2

    def test_empty_entities_returns_original(self):
        text = "No PII here"
        gen = TokenGenerator()
        masked, mapping, detected = anonymize(text, [], gen)

        assert masked == text
        assert mapping == {}
        assert detected == []


class TestDetokenize:
    def test_round_trip(self):
        text = "Contract for Hans Peter, IBAN CH9300762011623852957"
        mapping = {
            "[PERSON_1]": "Hans Peter",
            "[IBAN_1]": "CH9300762011623852957",
        }
        masked = "Contract for [PERSON_1], IBAN [IBAN_1]"
        result = detokenize(masked, mapping)
        assert result == text

    def test_handles_trailing_punctuation(self):
        mapping = {"[PERSON_1]": "Hans Peter"}
        masked = "Hello [PERSON_1], how are you?"
        result = detokenize(masked, mapping)
        assert result == "Hello Hans Peter, how are you?"

    def test_empty_mapping_returns_original(self):
        text = "No tokens here"
        assert detokenize(text, {}) == text

    def test_longer_tokens_replaced_first(self):
        mapping = {
            "[PERSON_1]": "Hans Peter",
            "[PERSON_1_EXTRA]": "Should not interfere",
        }
        masked = "Hello [PERSON_1]"
        result = detokenize(masked, mapping)
        assert "Hans Peter" in result
