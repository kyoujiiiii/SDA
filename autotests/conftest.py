"""Shared pytest fixtures for SDA autotests."""

import sys
from pathlib import Path

import pytest

# Ensure project root is importable
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def sample_texts():
    """Common test texts with various PII types."""
    return {
        "simple_pii": "Contact Hans Peter at hans.peter@example.com or call +41 79 123 45 67",
        "swiss_iban": "Transfer 500,000 CHF to IBAN CH93 0076 2011 6238 5295 7",
        "swiss_ahv": "Employee AHV number is 756.1234.5678.90",
        "multi_entity": (
            "Invoice for Hans Peter (hans@example.com), "
            "amount CHF 1,234.56, IBAN CH9300762011623852957, "
            "AHV 756.1234.5678.90, IP 192.168.1.100"
        ),
        "clean_text": "This sentence has no sensitive data at all.",
        "edge_empty": "",
        "edge_whitespace": "   \t\n   ",
    }
