"""Safety validation helpers for clinician-facing text."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER

DISALLOWED_CLINICAL_RECOMMENDATION_PHRASES: tuple[str, ...] = (
    "diagnosis",
    "treat",
    "therapy",
    "diagnosed with",
    "prescribe",
    "start treatment",
    "must treat",
    "should start",
    "medication adjustment",
    "lipid-lowering therapy",
    "therapy may be warranted",
    "requires treatment",
)

_DISALLOWED_CLINICAL_RECOMMENDATION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (phrase, re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE))
    for phrase in DISALLOWED_CLINICAL_RECOMMENDATION_PHRASES
)


def find_disallowed_clinical_phrases(text: str) -> list[str]:
    """Return disallowed clinical recommendation phrases found in text."""

    validated_text = re.sub(
        re.escape(CLINICIAN_REVIEW_DISCLAIMER),
        "",
        text,
        flags=re.IGNORECASE,
    )
    return [
        phrase
        for phrase, pattern in _DISALLOWED_CLINICAL_RECOMMENDATION_PATTERNS
        if pattern.search(validated_text)
    ]


def validate_clinician_facing_text(text: str) -> list[str]:
    """Return safety validation issues for a clinician-facing text string."""

    return find_disallowed_clinical_phrases(text)


def assert_clinician_facing_text_safe(text: str) -> None:
    """Raise if text contains disallowed recommendation language."""

    disallowed_phrases = validate_clinician_facing_text(text)
    if disallowed_phrases:
        phrase_list = ", ".join(disallowed_phrases)
        raise ValueError(f"Clinician-facing text contains disallowed phrase(s): {phrase_list}")


def assert_disclaimer_present(payload: Mapping[str, Any]) -> None:
    """Raise if a clinician-facing payload does not include the shared disclaimer."""

    if payload.get("disclaimer") != CLINICIAN_REVIEW_DISCLAIMER:
        raise ValueError("Clinician-facing payload must include the shared disclaimer.")


def assert_clinician_facing_payload_safe(payload: Mapping[str, Any]) -> None:
    """Raise if any string value in a payload contains disallowed language."""

    for text in _iter_string_values(payload):
        assert_clinician_facing_text_safe(text)


def _iter_string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            if key == "blocked_phrases":
                continue
            yield from _iter_string_values(child)
    elif isinstance(value, list | tuple):
        for child in value:
            yield from _iter_string_values(child)
