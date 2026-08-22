"""
Token generation, anonymization, and detokenization logic.
Pure algorithm — no external service dependencies.
"""

import re
from typing import Dict, List, Tuple

from .patterns import TOKEN_LABELS


class TokenGenerator:
    """Generates sequential tokens like [PERSON_1], [IBAN_2], etc."""

    def __init__(self):
        self._counters: Dict[str, int] = {}

    def next_token(self, entity_type: str) -> str:
        if entity_type not in self._counters:
            self._counters[entity_type] = 0
        self._counters[entity_type] += 1
        label = TOKEN_LABELS.get(entity_type, entity_type)
        return f"[{label}_{self._counters[entity_type]}]"

    def reset(self):
        self._counters.clear()


def anonymize(
    text: str,
    entities: list,
    generator: TokenGenerator,
) -> Tuple[str, Dict[str, str], List[Dict]]:
    """
    Replace detected entities with sequential tokens.

    Args:
        text: Original text
        entities: List of RecognizerResult-like objects (with .start, .end, .entity_type, .score)
        generator: TokenGenerator instance

    Returns:
        (anonymized_text, token_mapping, detected_entities_list)
    """
    generator.reset()

    if not entities:
        return text, {}, []

    # Sort by start position
    sorted_entities = sorted(entities, key=lambda e: e.start)

    token_mapping: Dict[str, str] = {}
    detected_entities: List[Dict] = []

    for entity in sorted_entities:
        original_value = text[entity.start:entity.end]
        token = generator.next_token(entity.entity_type)
        token_mapping[token] = original_value
        detected_entities.append({
            "entity_type": entity.entity_type,
            "start": entity.start,
            "end": entity.end,
            "original_value": original_value,
            "token": token,
            "score": entity.score,
        })

    # Replace in reverse order to preserve positions
    anonymized = text
    for entity in reversed(detected_entities):
        anonymized = (
            anonymized[:entity["start"]]
            + entity["token"]
            + anonymized[entity["end"]:]
        )

    return anonymized, token_mapping, detected_entities


def detokenize(text: str, token_mapping: Dict[str, str]) -> str:
    """
    Replace tokens with original values, handling trailing punctuation.

    e.g. [PERSON_1]. → Hans Peter.
    """
    result = text
    sorted_tokens = sorted(token_mapping.keys(), key=len, reverse=True)

    for token in sorted_tokens:
        original_value = token_mapping[token]
        escaped_token = re.escape(token)
        # Handle token followed by punctuation
        result = re.sub(
            rf"{escaped_token}([.,;:!?])",
            rf"{original_value}\1",
            result,
        )
        result = result.replace(token, original_value)

    return result
