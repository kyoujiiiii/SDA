"""
Regex patterns and token labels for PII detection.
Swiss-specific: IBAN (CH...), AHV/AVS (756.xxxx.xxxx.xx).
"""

from presidio_analyzer import Pattern


TOKEN_LABELS = {
    "PERSON": "PERSON",
    "EMAIL_ADDRESS": "EMAIL",
    "PHONE_NUMBER": "PHONE",
    "LOCATION": "LOCATION",
    "IBAN": "IBAN",
    "AHV_NUMBER": "AHV",
    "CREDIT_CARD": "CARD",
    "IP_ADDRESS": "IP",
    "AMOUNT": "AMOUNT",
}

SWISS_IBAN_PATTERNS = [
    Pattern(
        name="swiss_iban_spaced",
        regex=r"\bCH\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{1,4}\b",
        score=0.95,
    ),
    Pattern(
        name="swiss_iban_no_spaces",
        regex=r"\bCH\d{19}\b",
        score=0.9,
    ),
    Pattern(
        name="swiss_iban_flexible",
        regex=r"\bCH\d{2}(?:\s?\d{4}){4,5}\b",
        score=0.85,
    ),
]

SWISS_AHV_PATTERNS = [
    Pattern(
        name="swiss_ahv_dotted",
        regex=r"\b756\.\d{4}\.\d{4}\.\d{2}\b",
        score=0.95,
    ),
    Pattern(
        name="swiss_ahv_no_dots",
        regex=r"\b756\d{10}\b",
        score=0.8,
    ),
]
