"""Helpers for building PHI-safe structured log events."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REDACTED_VALUE = "[REDACTED]"
OMITTED_VALUE = "[OMITTED]"

SENSITIVE_FIELD_NAMES = {
    "authorization",
    "access_token",
    "api_key",
    "fhir_access_token",
    "gemini_api_key",
    "patient_address",
    "patient_birth_date",
    "patient_name",
    "patient_phone",
    "refresh_token",
    "secret",
    "x-fhir-access-token",
}


def build_safe_log_event(
    event_name: str,
    fields: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a structured event that redacts tokens and omits payload-shaped values."""

    return {
        "event": event_name.strip() or "unnamed_event",
        "fields": redact_sensitive_log_fields(fields or {}),
    }


def redact_sensitive_log_fields(fields: Mapping[str, Any]) -> dict[str, Any]:
    """Redact known-sensitive fields and omit nested payloads from log metadata."""

    redacted: dict[str, Any] = {}
    for key, value in fields.items():
        normalized_key = str(key).lower()
        if _is_sensitive_key(normalized_key):
            redacted[str(key)] = REDACTED_VALUE
        elif isinstance(value, str | int | float | bool) or value is None:
            redacted[str(key)] = value
        else:
            redacted[str(key)] = OMITTED_VALUE
    return redacted


def _is_sensitive_key(normalized_key: str) -> bool:
    return (
        normalized_key in SENSITIVE_FIELD_NAMES
        or "token" in normalized_key
        or "authorization" in normalized_key
        or "secret" in normalized_key
        or "api_key" in normalized_key
        or "fhir_payload" in normalized_key
        or "raw_fhir" in normalized_key
    )
