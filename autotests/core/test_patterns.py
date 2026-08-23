"""Tests for core.patterns — regex patterns and token labels."""

import re

import pytest

from core.patterns import (
    TOKEN_LABELS,
    SWISS_IBAN_PATTERNS,
    SWISS_AHV_PATTERNS,
)


class TestTokenLabels:
    def test_labels_has_required_entities(self):
        required = {"PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "IBAN", "AHV_NUMBER"}
        assert required.issubset(set(TOKEN_LABELS.keys()))

    def test_labels_are_strings(self):
        for key, val in TOKEN_LABELS.items():
            assert isinstance(key, str)
            assert isinstance(val, str)


class TestSwissIBANPatterns:
    @pytest.mark.parametrize("iban", [
        "CH9300762011623852957",
        "CH93 0076 2011 6238 5295 7",
        "CH930076201162385295",
        "CH1234567890123456789",
    ])
    def test_valid_swiss_iban_matches(self, iban):
        combined = "|".join(p.regex for p in SWISS_IBAN_PATTERNS)
        assert re.search(combined, iban), f"Should match: {iban}"

    @pytest.mark.parametrize("not_iban", [
        "DE89370400440532013000",  # German IBAN
        "CH",                       # Too short
        "GB29NWBK60161331926819",  # UK IBAN
    ])
    def test_invalid_iban_no_match(self, not_iban):
        combined = "|".join(p.regex for p in SWISS_IBAN_PATTERNS)
        assert not re.search(combined, not_iban), f"Should NOT match: {not_iban}"


class TestSwissAHVPatterns:
    @pytest.mark.parametrize("ahv", [
        "756.1234.5678.90",
        "7561234567890",
    ])
    def test_valid_swiss_ahv_matches(self, ahv):
        combined = "|".join(p.regex for p in SWISS_AHV_PATTERNS)
        assert re.search(combined, ahv), f"Should match: {ahv}"

    @pytest.mark.parametrize("not_ahv", [
        "756.1234.5678.9",    # Too short
        "757.1234.5678.90",   # Wrong prefix
        "756123456789",       # Wrong length
    ])
    def test_invalid_ahv_no_match(self, not_ahv):
        combined = "|".join(p.regex for p in SWISS_AHV_PATTERNS)
        assert not re.search(combined, not_ahv), f"Should NOT match: {not_ahv}"
