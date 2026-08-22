"""
AirlockEngine — single entry point for PII masking/demasking.
Facade over detector + tokenizer. No session/state logic.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from .detector import detect_entities
from .tokenizer import TokenGenerator, anonymize, detokenize


@dataclass
class DetectedEntity:
    """One detected PII entity."""
    entity_type: str
    start: int
    end: int
    original_value: str
    token: str
    score: float


@dataclass
class MaskResult:
    """Result of masking a text."""
    masked_text: str
    mapping: Dict[str, str]
    entities: List[DetectedEntity]


class AirlockEngine:
    """
    Pure algorithm facade for PII detection, masking, and demasking.

    Usage:
        engine = AirlockEngine()
        result = engine.mask("Contract for Hans Peter, IBAN CH9300000000000000000")
        clean = engine.unmask(result.masked_text, result.mapping)
    """

    def __init__(self):
        self._generator = TokenGenerator()

    def mask(self, text: str, language: str = "en") -> MaskResult:
        """
        Detect PII and replace with tokens.

        Returns MaskResult with masked_text, mapping, and detected entities.
        """
        entities = detect_entities(text, language)
        masked_text, mapping, raw_entities = anonymize(text, entities, self._generator)

        return MaskResult(
            masked_text=masked_text,
            mapping=mapping,
            entities=[
                DetectedEntity(**e) for e in raw_entities
            ],
        )

    def unmask(self, text: str, mapping: Dict[str, str]) -> str:
        """Restore original values from token mapping."""
        return detokenize(text, mapping)
