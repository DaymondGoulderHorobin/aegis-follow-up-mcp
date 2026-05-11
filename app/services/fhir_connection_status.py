"""FHIR connection transparency for Prompt Opinion demos."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.config import settings
from app.fhir.context import get_runtime_fhir_context
from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)


def get_fhir_connection_status(
    patient_id: str | None = None,
    headers: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Report FHIR-context header presence and optional connectivity support."""

    context = get_runtime_fhir_context(headers)
    server_url_present = bool(context.server_url)
    access_token_present = bool(context.access_token)
    context_patient_present = bool(context.patient_id)
    resolved_patient_id = patient_id or context.patient_id
    fhir_context_received = any(
        [server_url_present, access_token_present, context_patient_present]
    )
    live_fhir_reads_enabled = settings.live_fhir_reads_enabled and not context.fixture_mode
    active_data_source = "synthetic_fixture_data"
    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "fixture_mode": active_data_source == "synthetic_fixture_data",
        "fhir_context_received": fhir_context_received,
        "server_url_present": server_url_present,
        "access_token_present": access_token_present,
        "patient_id_present": bool(resolved_patient_id),
        "patient_id_source": _patient_id_source(patient_id, context.patient_id),
        "live_fhir_reads_enabled": live_fhir_reads_enabled,
        "live_fhir_connectivity_check_supported": settings.live_fhir_reads_enabled,
        "connectivity_proof_tool": "validate_fhir_context_connection",
        "connectivity_proof_can_attempt": live_fhir_reads_enabled,
        "active_data_source": active_data_source,
        "clinical_workflow_source": active_data_source,
        "notes": _notes(
            fhir_context_received=fhir_context_received,
            active_data_source=active_data_source,
            connectivity_proof_can_attempt=live_fhir_reads_enabled,
        ),
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload


def _patient_id_source(
    explicit_patient_id: str | None,
    context_patient_id: str | None,
) -> str:
    if explicit_patient_id:
        return "explicit_tool_argument"
    if context_patient_id:
        return "fhir_context_header"
    return "not_provided"


def _notes(
    fhir_context_received: bool,
    active_data_source: str,
    connectivity_proof_can_attempt: bool,
) -> list[str]:
    if active_data_source == "external_fhir_server":
        return [
            "FHIR context is complete and live reads are enabled.",
            "Access token presence is reported only as a boolean.",
        ]
    if connectivity_proof_can_attempt:
        return [
            "FHIR context is complete and the optional connectivity proof can attempt "
            "a read-only Patient lookup.",
            "Core demo workflow still uses synthetic fixture data.",
            "Access token presence is reported only as a boolean.",
        ]
    if fhir_context_received:
        return [
            "FHIR context header presence was detected.",
            "Demo mode still uses synthetic fixture data.",
            "Access token presence is reported only as a boolean.",
        ]
    return [
        "Demo mode uses synthetic fixture data.",
        "No real PHI is required for hackathon validation.",
    ]
