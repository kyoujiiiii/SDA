# Core — PII Masking Algorithm

Pure algorithm for detecting, masking, and restoring sensitive data (PII).

## Quick Start

```python
from core import AirlockEngine

engine = AirlockEngine()

# Mask sensitive data
result = engine.mask("Contract for Hans Peter, IBAN CH9300000000000000000")

print(result.masked_text)
# → "Contract for [PERSON_1], IBAN [IBAN_1]"

print(result.mapping)
# → {"[PERSON_1]": "Hans Peter", "[IBAN_1]": "CH9300000000000000000"}

# Restore original values (for authorized users)
clean = engine.unmask(result.masked_text, result.mapping)
# → "Contract for Hans Peter, IBAN CH9300000000000000000"
```

## API

### `AirlockEngine`

The single entry point. Create one instance and reuse it.

| Method | Input | Output |
|--------|-------|--------|
| `mask(text)` | original text | `MaskResult` |
| `unmask(text, mapping)` | masked text + mapping dict | restored string |

### `MaskResult`

Returned by `engine.mask()`:

| Field | Type | Description |
|-------|------|-------------|
| `masked_text` | `str` | Text with tokens (`[PERSON_1]`, `[IBAN_1]`, etc.) |
| `mapping` | `Dict[str, str]` | Token → original value (`{"[PERSON_1]": "Hans Peter"}`) |
| `entities` | `List[DetectedEntity]` | All detected PII with positions and scores |

### `DetectedEntity`

One detected PII item:

| Field | Type | Example |
|-------|------|---------|
| `entity_type` | `str` | `"PERSON"`, `"IBAN"`, `"EMAIL_ADDRESS"` |
| `start` | `int` | Character position where entity starts |
| `end` | `int` | Character position where entity ends |
| `original_value` | `str` | `"Hans Peter"` |
| `token` | `str` | `"[PERSON_1]"` |
| `score` | `float` | Confidence `0.0` – `1.0` |

## Detected Entity Types

| Type | Token Format | Example |
|------|-------------|---------|
| Person | `[PERSON_N]` | `[PERSON_1]` |
| Email | `[EMAIL_N]` | `[EMAIL_1]` |
| Phone | `[PHONE_N]` | `[PHONE_1]` |
| Location | `[LOCATION_N]` | `[LOCATION_1]` |
| Swiss IBAN | `[IBAN_N]` | `[IBAN_1]` |
| Swiss AHV | `[AHV_N]` | `[AHV_1]` |
| Credit Card | `[CARD_N]` | `[CARD_1]` |
| IP Address | `[IP_N]` | `[IP_1]` |

## Integration Pattern

```
Frontend  →  FastAPI (main.py)  →  services/  →  core/
                                       │            │
                              vault_service    AirlockEngine
                              llm_service        mask()
                                                unmask()
```

**Service layer** (`services/presidio_service.py`) wraps core and exposes:
- `presidio_service.anonymize_text(text)` → returns `DetectionResult`
- `presidio_service.detokenize_text(text, mapping)` → returns restored string

**Frontend** talks to FastAPI endpoints, which use services, which use core.

## Example: Frontend Data Flow

```python
# 1. User sends prompt from frontend
prompt = "Send CHF 50,000 to Hans Peter, IBAN CH9300000000000000000"

# 2. Backend masks before sending to LLM
result = engine.mask(prompt)
llm_response = call_llm(result.masked_text)

# 3. If user is admin → restore original values
if role == "admin":
    final = engine.unmask(llm_response, result.mapping)
else:
    final = llm_response  # auditor sees masked version
```

## Files

| File | Purpose |
|------|---------|
| `engine.py` | `AirlockEngine` facade — main entry point |
| `detector.py` | PII detection (Presidio + Swiss regex) |
| `tokenizer.py` | Token generation, anonymize, detokenize |
| `patterns.py` | Regex patterns and token labels |
