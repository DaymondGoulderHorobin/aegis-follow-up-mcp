"""FastMCP tool registration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover - normal in lightweight local test envs
    FastMCP = None

from app.config import settings
from app.fhir.context import resolve_patient_id
from app.prompt_opinion.fhir_context_extension import (
    build_capabilities_extensions,
    install_fhir_context_extension,
)
from app.services.abnormal_results import find_unresolved_abnormal_results as find_results
from app.services.ai_follow_up_brief import generate_ai_follow_up_brief as build_ai_brief
from app.services.audit_trail import explain_result_decisions as build_audit_trail
from app.services.brief_generator import generate_follow_up_brief as build_brief
from app.services.ehr_integration import get_ehr_integration_summary as build_ehr_summary
from app.services.fhir_connection_status import (
    get_fhir_connection_status as build_fhir_status,
)
from app.services.fhir_connectivity import (
    validate_fhir_context_connection as build_fhir_connectivity_proof,
)
from app.services.follow_up_priority import assess_follow_up_priority as build_priority
from app.services.follow_up_tasks import list_follow_up_tasks as build_task_queue
from app.services.handoff_payload import create_follow_up_handoff_payload as build_handoff
from app.services.note_drafter import draft_clinician_note as build_note
from app.services.observations import get_recent_observations as build_observations
from app.services.patient_snapshot import get_patient_snapshot as build_snapshot
from app.services.rule_profiles import list_rule_profiles as build_rule_profiles
from app.services.workflow_state import update_follow_up_task_status as build_status_update


class LocalMCPRegistry:
    """Fallback registry used when FastMCP is not installed."""

    def __init__(self, name: str):
        self.name = name
        self.tools: dict[str, Callable[..., Any]] = {}
        self.capabilities_extensions = build_capabilities_extensions()

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


def _create_mcp() -> Any:
    if FastMCP is None:
        return LocalMCPRegistry(settings.project_name)
    fastmcp_server = FastMCP(settings.project_name, version=settings.version)
    install_fhir_context_extension(fastmcp_server)
    return fastmcp_server


mcp = _create_mcp()
_REGISTERED_TOOL_NAMES: list[str] = []


def _register_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    _REGISTERED_TOOL_NAMES.append(func.__name__)
    return mcp.tool()(func)


@_register_tool
def get_patient_snapshot(patient_id: str | None = None) -> dict[str, Any]:
    """Return synthetic patient demographics, conditions, medications, and encounters."""

    return build_snapshot(patient_id=resolve_patient_id(patient_id)).model_dump()


@_register_tool
def get_recent_observations(patient_id: str | None = None) -> list[dict[str, Any]]:
    """Return recent synthetic observations and lab results."""

    resolved_patient_id = resolve_patient_id(patient_id)
    return [
        observation.model_dump()
        for observation in build_observations(patient_id=resolved_patient_id)
    ]


@_register_tool
def find_unresolved_abnormal_results(patient_id: str | None = None) -> list[dict[str, Any]]:
    """Flag abnormal results with no obvious follow-up evidence in synthetic data."""

    resolved_patient_id = resolve_patient_id(patient_id)
    return [finding.model_dump() for finding in find_results(patient_id=resolved_patient_id)]


@_register_tool
def generate_follow_up_brief(patient_id: str | None = None) -> dict[str, Any]:
    """Generate a deterministic clinician-facing follow-up brief."""

    return build_brief(patient_id=resolve_patient_id(patient_id))


@_register_tool
def generate_ai_follow_up_brief(
    patient_id: str | None = None,
    profile_id: str = "default_primary_care",
) -> dict[str, Any]:
    """Generate an optional AI narrative with deterministic guardrails and fallback."""

    return build_ai_brief(
        patient_id=resolve_patient_id(patient_id),
        profile_id=profile_id,
    )


@_register_tool
def draft_clinician_note(patient_id: str | None = None) -> dict[str, str]:
    """Draft a short note for clinician review."""

    return {"draft_note": build_note(patient_id=resolve_patient_id(patient_id))}


@_register_tool
def assess_follow_up_priority(
    patient_id: str | None = None,
    profile_id: str = "default_primary_care",
) -> dict[str, Any]:
    """Assess deterministic clinician-review priority for unresolved abnormalities."""

    return build_priority(patient_id=resolve_patient_id(patient_id), profile_id=profile_id)


@_register_tool
def list_rule_profiles() -> dict[str, Any]:
    """Return available deterministic rule profiles."""

    return build_rule_profiles()


@_register_tool
def explain_result_decisions(
    patient_id: str | None = None,
    profile_id: str = "default_primary_care",
) -> dict[str, Any]:
    """Return audit decisions explaining flagged and suppressed synthetic results."""

    return build_audit_trail(
        patient_id=resolve_patient_id(patient_id),
        profile_id=profile_id,
    )


@_register_tool
def list_follow_up_tasks(
    profile_id: str = "default_primary_care",
    patient_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Return a priority-grouped synthetic follow-up task queue."""

    return build_task_queue(profile_id=profile_id, patient_ids=patient_ids)


@_register_tool
def get_fhir_connection_status(patient_id: str | None = None) -> dict[str, Any]:
    """Report fixture-versus-FHIR context status without live clinical reads."""

    return build_fhir_status(patient_id=patient_id)


@_register_tool
def validate_fhir_context_connection() -> dict[str, Any]:
    """Optionally prove FHIR Patient reachability with safe metadata only."""

    return build_fhir_connectivity_proof()


@_register_tool
def create_follow_up_handoff_payload(
    patient_id: str | None = "synthetic-patient-003",
    profile_id: str = "default_primary_care",
) -> dict[str, Any]:
    """Create a payload-only follow-up handoff for future agent workflows."""

    return build_handoff(
        patient_id=patient_id,
        profile_id=profile_id,
    )


@_register_tool
def update_follow_up_task_status(
    task_id: str,
    status: str,
    reason: str | None = None,
) -> dict[str, Any]:
    """Simulate clinician review state without writing to an EHR."""

    return build_status_update(task_id=task_id, status=status, reason=reason)


@_register_tool
def get_ehr_integration_summary() -> dict[str, Any]:
    """Return the current and future EHR integration story."""

    return build_ehr_summary()


def get_registered_tool_names() -> list[str]:
    return list(_REGISTERED_TOOL_NAMES)


def get_capabilities_extensions() -> dict[str, Any]:
    return build_capabilities_extensions()


def get_mcp_asgi_app() -> Any | None:
    """Return a FastMCP ASGI app when supported by the installed package."""

    if FastMCP is None:
        return None

    for method_name in ("http_app", "streamable_http_app", "sse_app"):
        method = getattr(mcp, method_name, None)
        if not callable(method):
            continue
        try:
            if method_name == "http_app":
                return method(
                    path="/",
                    transport=settings.mcp_transport,
                    json_response=settings.mcp_json_response,
                    stateless_http=settings.mcp_stateless_http,
                )
            return method(path="/")
        except TypeError:
            return method()
    return None
