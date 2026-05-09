"""FHIR context parsing.

The access token is carried in memory only and should not be logged.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

try:
    from fastmcp.server.dependencies import get_http_headers
except ImportError:  # pragma: no cover - used only when FastMCP is unavailable

    def get_http_headers() -> dict[str, str]:
        return {}

FHIR_SERVER_HEADER = "x-fhir-server-url"
FHIR_TOKEN_HEADER = "x-fhir-access-token"
FHIR_PATIENT_HEADER = "x-patient-id"


@dataclass(frozen=True)
class FHIRContext:
    server_url: str | None = None
    access_token: str | None = field(default=None, repr=False)
    patient_id: str | None = None
    fixture_mode: bool = True

    @property
    def has_external_context(self) -> bool:
        return not self.fixture_mode

    def safe_summary(self) -> dict[str, str | bool | None]:
        return {
            "server_url": self.server_url,
            "patient_id": self.patient_id,
            "fixture_mode": self.fixture_mode,
            "access_token": "[REDACTED]" if self.access_token else None,
        }


def parse_fhir_context(headers: Mapping[str, str] | None) -> FHIRContext:
    """Parse Prompt Opinion/FHIR headers.

    Fixture mode is used unless all required external FHIR headers are present.
    """

    normalized_headers = {
        str(key).lower(): str(value)
        for key, value in (headers or {}).items()
        if value is not None
    }
    server_url = normalized_headers.get(FHIR_SERVER_HEADER)
    access_token = normalized_headers.get(FHIR_TOKEN_HEADER)
    patient_id = normalized_headers.get(FHIR_PATIENT_HEADER)
    fixture_mode = not all([server_url, access_token, patient_id])

    return FHIRContext(
        server_url=server_url,
        access_token=access_token,
        patient_id=patient_id,
        fixture_mode=fixture_mode,
    )


def get_runtime_fhir_context(headers: Mapping[str, str] | None = None) -> FHIRContext:
    """Resolve FHIR context from supplied or active FastMCP HTTP headers."""

    return parse_fhir_context(headers if headers is not None else get_http_headers())


def resolve_patient_id(
    explicit_patient_id: str | None = None,
    headers: Mapping[str, str] | None = None,
) -> str | None:
    """Prefer explicit tool argument, then Prompt Opinion/FHIR context header."""

    if explicit_patient_id:
        return explicit_patient_id
    return get_runtime_fhir_context(headers).patient_id
