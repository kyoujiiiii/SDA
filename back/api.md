# Swiss Data Airlock — Core Engine API

Pure Python library for detecting, masking, and restoring sensitive data (PII). Built on Microsoft Presidio with native Swiss pattern support (IBAN, AHV/AVS).

## Dependencies

```
presidio-analyzer
spacy
```

Required spaCy model:

```bash
python -m spacy download en_core_web_lg
```

## Quick Start

```python
from core import AirlockEngine

engine = AirlockEngine()

# Mask sensitive data
result = engine.mask("Send CHF 50k to Hans Peter, IBAN CH9300000000000000000")
print(result.masked_text)
# → "Send CHF 50k to [PERSON_1], IBAN [IBAN_1]"

# Restore original values (authorized access only)
clean = engine.unmask(result.masked_text, result.mapping)
# → "Send CHF 50k to Hans Peter, IBAN CH9300000000000000000"
```

## Core API

### `AirlockEngine`

The single entry point. Create one instance and reuse it across your application.

```python
engine = AirlockEngine()
```

#### `engine.mask(text, language="en")`

Detect all PII in `text` and replace with sequential tokens.

| Parameter  | Type  | Default | Description |
|------------|-------|---------|-------------|
| `text`     | `str` | —       | Input text containing potential PII |
| `language` | `str` | `"en"`  | Language code for NLP analysis |

**Returns:** `MaskResult`

```python
result = engine.mask("Email hans@example.com or call +41 79 123 45 67")

result.masked_text
# → "Email [EMAIL_1] or call [PHONE_1]"

result.mapping
# → {"[EMAIL_1]": "hans@example.com", "[PHONE_1]": "+41 79 123 45 67"}

result.entities[0].entity_type
# → "EMAIL_ADDRESS"
```

#### `engine.unmask(text, mapping)`

Restore original values from a token mapping.

| Parameter | Type               | Description |
|-----------|--------------------|-------------|
| `text`    | `str`              | Masked text containing tokens |
| `mapping` | `Dict[str, str]`  | Token → original value mapping |

**Returns:** `str` — restored original text

```python
clean = engine.unmask(
    "Contact [PERSON_1] at [EMAIL_1]",
    {"[PERSON_1]": "Hans Peter", "[EMAIL_1]": "hans@example.com"}
)
# → "Contact Hans Peter at hans@example.com"
```

Handles trailing punctuation automatically: `[PERSON_1].` → `Hans Peter.`

---

## Data Types

### `MaskResult`

Returned by `engine.mask()`.

| Field      | Type                    | Description |
|------------|-------------------------|-------------|
| `masked_text` | `str`                | Text with tokens replacing PII |
| `mapping`     | `Dict[str, str]`    | Token → original value (`{"[PERSON_1]": "Hans Peter"}`) |
| `entities`    | `List[DetectedEntity]` | All detected PII items with positions |

### `DetectedEntity`

One detected PII item.

| Field            | Type    | Description |
|------------------|---------|-------------|
| `entity_type`    | `str`   | PII category: `"PERSON"`, `"EMAIL_ADDRESS"`, `"IBAN"`, etc. |
| `start`          | `int`   | Character offset where entity begins |
| `end`            | `int`   | Character offset where entity ends (exclusive) |
| `original_value` | `str`   | The actual PII text (`"Hans Peter"`) |
| `token`          | `str`   | Replacement token (`"[PERSON_1]"`) |
| `score`          | `float` | Confidence score `0.0` – `1.0` |

---

## Supported Entity Types

| Type         | Presidio Entity     | Token Format   | Example Input                        |
|--------------|---------------------|----------------|--------------------------------------|
| Person       | `PERSON`            | `[PERSON_N]`   | `Hans Peter`                         |
| Email        | `EMAIL_ADDRESS`     | `[EMAIL_N]`    | `hans@example.com`                   |
| Phone        | `PHONE_NUMBER`      | `[PHONE_N]`    | `+41 79 123 45 67`                   |
| Location     | `LOCATION`          | `[LOCATION_N]` | `Bahnhofstrasse 1, Zurich`           |
| Swiss IBAN   | `IBAN`              | `[IBAN_N]`     | `CH9300000000000000000`              |
| Swiss AHV    | `AHV_NUMBER`        | `[AHV_N]`      | `756.1234.5678.90`                   |
| Credit Card  | `CREDIT_CARD`       | `[CARD_N]`     | `4111 1111 1111 1111`                |
| IP Address   | `IP_ADDRESS`        | `[IP_N]`       | `192.168.1.1`                        |

---

## Low-Level API

For advanced use cases where you need direct control over detection or tokenization.

### `detect_entities(text, language="en")`

Run PII detection without masking. Returns raw Presidio `RecognizerResult` objects.

```python
from core import detect_entities

results = detect_entities("IBAN CH9300000000000000000")
# → [RecognizerResult(entity_type='IBAN', start=5, end=24, score=0.95)]
```

### `anonymize(text, entities, generator)`

Replace detected entities with tokens. Used internally by `AirlockEngine.mask()`.

| Parameter   | Type              | Description |
|-------------|-------------------|-------------|
| `text`      | `str`             | Original text |
| `entities`  | `list`            | Output from `detect_entities()` |
| `generator` | `TokenGenerator`  | Token name generator |

**Returns:** `(anonymized_text, token_mapping, detected_entities_list)`

### `detokenize(text, token_mapping)`

Replace tokens with original values. Used internally by `AirlockEngine.unmask()`.

### `TokenGenerator`

Creates sequential tokens like `[PERSON_1]`, `[PERSON_2]`, `[IBAN_1]`.

```python
from core import TokenGenerator

gen = TokenGenerator()
gen.next_token("PERSON")  # → "[PERSON_1]"
gen.next_token("PERSON")  # → "[PERSON_2]"
gen.next_token("IBAN")    # → "[IBAN_1]"
gen.reset()               # → counters reset to 0
```

---

## Integration Examples

### Batch Processing

```python
from core import AirlockEngine

engine = AirlockEngine()

texts = [
    "Invoice for Hans Peter, IBAN CH9300000000000000000",
    "Contact maria@example.com for details",
    "Employee AHV: 756.1234.5678.90",
]

results = []
for text in texts:
    r = engine.mask(text)
    results.append(r)
    # Send r.masked_text to your external service...

# Later, restore a specific result
restored = engine.unmask(results[0].masked_text, results[0].mapping)
```

### Role-Based Access

```python
from core import AirlockEngine

engine = AirlockEngine()
result = engine.mask("Payment of CHF 10k to Hans Peter (IBAN CH9300000000000000000)")

# Admin (data owner) — sees real values
admin_view = engine.unmask(result.masked_text, result.mapping)

# Auditor — sees only masked version (no mapping provided)
auditor_view = result.masked_text
```

### Passing to External LLM

```python
from core import AirlockEngine

engine = AirlockEngine()
result = engine.mask(user_prompt)

# Send masked text to LLM — no PII exposed
llm_response = call_external_llm(result.masked_text)

# Restore PII in LLM response (if authorized)
final = engine.unmask(llm_response, result.mapping)
```

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No PII found | `mask()` returns original text, empty mapping, empty entity list |
| Empty string | Same as no PII — returns `("", {}, [])` |
| Unknown token in `unmask()` | Token is left unchanged in output |
| Mapping key mismatch | Unmatched tokens pass through as-is |

---

## File Reference

| File          | Purpose |
|---------------|---------|
| `engine.py`   | `AirlockEngine` — main facade |
| `detector.py` | Presidio detection with Swiss custom recognizers |
| `tokenizer.py`| Token generation, anonymize/detokenize logic |
| `patterns.py` | Regex patterns and token label mappings |
