"""Redaction utilities for logs and diagnostics."""

from __future__ import annotations

from collections.abc import Mapping

SENSITIVE_HEADER_NAMES = {
    "authorization",
    "x-fhir-access-token",
    "x-refresh-token",
}


def redact_headers(headers: Mapping[str, str] | None) -> dict[str, str]:
    redacted: dict[str, str] = {}
    for key, value in (headers or {}).items():
        if key.lower() in SENSITIVE_HEADER_NAMES:
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted
