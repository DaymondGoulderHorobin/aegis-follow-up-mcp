"""FastMCP tool registration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover - normal in lightweight local test envs
    FastMCP = None

from app.config import settings
from app.services.abnormal_results import find_unresolved_abnormal_results as find_results
from app.services.brief_generator import generate_follow_up_brief as build_brief
from app.services.note_drafter import draft_clinician_note as build_note
from app.services.observations import get_recent_observations as build_observations
from app.services.patient_snapshot import get_patient_snapshot as build_snapshot


class LocalMCPRegistry:
    """Fallback registry used when FastMCP is not installed."""

    def __init__(self, name: str):
        self.name = name
        self.tools: dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


def _create_mcp() -> Any:
    if FastMCP is None:
        return LocalMCPRegistry(settings.project_name)
    return FastMCP(settings.project_name)


mcp = _create_mcp()
_REGISTERED_TOOL_NAMES: list[str] = []


def _register_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    _REGISTERED_TOOL_NAMES.append(func.__name__)
    return mcp.tool()(func)


@_register_tool
def get_patient_snapshot(patient_id: str | None = None) -> dict[str, Any]:
    """Return synthetic patient demographics, conditions, medications, and encounters."""

    return build_snapshot(patient_id=patient_id).model_dump()


@_register_tool
def get_recent_observations(patient_id: str | None = None) -> list[dict[str, Any]]:
    """Return recent synthetic observations and lab results."""

    return [observation.model_dump() for observation in build_observations(patient_id=patient_id)]


@_register_tool
def find_unresolved_abnormal_results(patient_id: str | None = None) -> list[dict[str, Any]]:
    """Flag abnormal results with no obvious follow-up evidence in synthetic data."""

    return [finding.model_dump() for finding in find_results(patient_id=patient_id)]


@_register_tool
def generate_follow_up_brief(patient_id: str | None = None) -> dict[str, Any]:
    """Generate a deterministic clinician-facing follow-up brief."""

    return build_brief(patient_id=patient_id)


@_register_tool
def draft_clinician_note(patient_id: str | None = None) -> dict[str, str]:
    """Draft a short note for clinician review."""

    return {"draft_note": build_note(patient_id=patient_id)}


def get_registered_tool_names() -> list[str]:
    return list(_REGISTERED_TOOL_NAMES)


def get_mcp_asgi_app() -> Any | None:
    """Return a FastMCP ASGI app when supported by the installed package."""

    if FastMCP is None:
        return None

    for method_name in ("http_app", "streamable_http_app", "sse_app"):
        method = getattr(mcp, method_name, None)
        if not callable(method):
            continue
        try:
            return method(path="/")
        except TypeError:
            return method()
    return None
