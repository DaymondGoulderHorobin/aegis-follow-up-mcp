"""Safe, narrow FHIR connectivity proof for Prompt Opinion demos."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from contextlib import AbstractContextManager
from typing import Any

import httpx

from app.config import settings
from app.fhir.context import FHIRContext, get_runtime_fhir_context
from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)

FHIR_PATIENT_RESOURCE_TEMPLATE = "Patient/{patient_id}"
FHIR_CONNECTIVITY_TIMEOUT_SECONDS = 8.0

FHIRClientFactory = Callable[..., AbstractContextManager[httpx.Client]]


def validate_fhir_context_connection(
    headers: Mapping[str, str] | None = None,
    live_fhir_reads_enabled: bool | None = None,
    client_factory: FHIRClientFactory | None = None,
) -> dict[str, Any]:
    """Attempt a minimal read-only FHIR Patient lookup when explicitly enabled.

    This tool proves reachability only. It never returns the FHIR response body,
    token value, or patient demographics, and the clinical workflow remains backed
    by synthetic fixture data.
    """

    context = get_runtime_fhir_context(headers)
    live_reads_enabled = (
        settings.live_fhir_reads_enabled
        if live_fhir_reads_enabled is None
        else live_fhir_reads_enabled
    )
    payload = _base_payload(
        context=context,
        live_reads_enabled=live_reads_enabled and not context.fixture_mode,
    )

    if context.fixture_mode:
        payload.update(
            {
                "status": "not_attempted",
                "reason": "missing_fhir_context",
                "request_attempted": False,
            }
        )
        return _validated(payload)

    if not live_reads_enabled:
        payload.update(
            {
                "status": "not_attempted",
                "reason": "live_fhir_reads_disabled",
                "request_attempted": False,
                "live_fhir_reads_enabled": False,
            }
        )
        return _validated(payload)

    payload.update(
        {
            "request_attempted": True,
            "resource_requested": FHIR_PATIENT_RESOURCE_TEMPLATE,
        }
    )
    try:
        response = _fetch_patient(context, client_factory)
    except httpx.TimeoutException:
        payload.update({"status": "unreachable", "error_type": "timeout"})
        return _validated(payload)
    except httpx.HTTPError:
        payload.update({"status": "unreachable", "error_type": "network_error"})
        return _validated(payload)

    payload["http_status"] = response.status_code
    if response.status_code != 200:
        payload.update(
            {
                "status": "unreachable",
                "error_type": _error_type_for_status(response.status_code),
            }
        )
        return _validated(payload)

    resource_summary = _patient_resource_summary(response, context.patient_id)
    payload.update(resource_summary)
    if resource_summary["resource_type"] == "Patient":
        payload["status"] = "reachable"
    else:
        payload.update({"status": "unreachable", "error_type": "unexpected_resource"})
    return _validated(payload)


def _base_payload(context: FHIRContext, live_reads_enabled: bool) -> dict[str, Any]:
    return {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "status": "not_attempted",
        "request_attempted": False,
        "server_url_present": bool(context.server_url),
        "access_token_present": bool(context.access_token),
        "patient_id_present": bool(context.patient_id),
        "live_fhir_reads_enabled": live_reads_enabled,
        "token_disclosed": False,
        "payload_includes_phi": False,
        "clinical_workflow_source": "synthetic_fixture_data",
    }


def _fetch_patient(
    context: FHIRContext,
    client_factory: FHIRClientFactory | None,
) -> httpx.Response:
    if not context.server_url or not context.access_token or not context.patient_id:
        raise httpx.HTTPError("complete FHIR context is required")

    factory = client_factory or httpx.Client
    headers = {
        "Accept": "application/fhir+json, application/json",
        "Authorization": f"Bearer {context.access_token}",
    }
    with factory(
        base_url=context.server_url.rstrip("/"),
        timeout=FHIR_CONNECTIVITY_TIMEOUT_SECONDS,
        headers=headers,
    ) as client:
        return client.get(f"/Patient/{context.patient_id}")


def _patient_resource_summary(response: httpx.Response, patient_id: str | None) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError:
        body = {}
    resource_type = body.get("resourceType") if isinstance(body, dict) else None
    confirmed_id = bool(
        isinstance(body, dict)
        and resource_type == "Patient"
        and patient_id is not None
        and body.get("id") == patient_id
    )
    return {
        "resource_type": resource_type if isinstance(resource_type, str) else "unknown",
        "patient_id_confirmed": confirmed_id,
    }


def _error_type_for_status(status_code: int) -> str:
    if status_code in {401, 403}:
        return "authorization_failed"
    if status_code == 404:
        return "patient_not_found"
    if 400 <= status_code < 500:
        return "client_error"
    if 500 <= status_code < 600:
        return "server_error"
    return "unexpected_status"


def _validated(payload: dict[str, Any]) -> dict[str, Any]:
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload
