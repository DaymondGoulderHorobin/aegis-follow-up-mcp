"""Prompt Opinion FHIR-context MCP extension metadata."""

from __future__ import annotations

from functools import wraps
from typing import Any

PROMPT_OPINION_FHIR_CONTEXT_EXTENSION = "ai.promptopinion/fhir-context"

_DEFAULT_FHIR_CONTEXT_SCOPE_NAMES = (
    "patient/Patient.rs",
    "patient/Observation.rs",
    "patient/Condition.rs",
    "patient/MedicationStatement.rs",
    "patient/Encounter.rs",
)

DEFAULT_FHIR_CONTEXT_SCOPES: list[dict[str, str | bool]] = [
    {"name": scope_name, "required": False}
    for scope_name in _DEFAULT_FHIR_CONTEXT_SCOPE_NAMES
]


def build_fhir_context_extension() -> dict[str, list[dict[str, str | bool]]]:
    """Build Prompt Opinion FHIR-context extension params.

    All scopes are optional in Sprint 4 because the deterministic demo remains
    usable without external FHIR authorization.
    """

    return {"scopes": [scope.copy() for scope in DEFAULT_FHIR_CONTEXT_SCOPES]}


def build_capabilities_extensions() -> dict[str, dict[str, list[dict[str, str | bool]]]]:
    """Return MCP capabilities.extensions entries for Prompt Opinion."""

    return {
        PROMPT_OPINION_FHIR_CONTEXT_EXTENSION: build_fhir_context_extension(),
    }


def attach_fhir_context_extension(capabilities: Any) -> Any:
    """Attach Prompt Opinion FHIR-context metadata to a capabilities object."""

    existing_extensions = getattr(capabilities, "extensions", None)
    if existing_extensions is None:
        model_extra = getattr(capabilities, "model_extra", None) or {}
        existing_extensions = model_extra.get("extensions", {})

    if not isinstance(existing_extensions, dict):
        existing_extensions = {}

    capabilities.extensions = {
        **existing_extensions,
        **build_capabilities_extensions(),
    }
    return capabilities


def install_fhir_context_extension(mcp_server: Any) -> bool:
    """Install a FastMCP capabilities adapter when the runtime exposes one.

    FastMCP 3.2.4 does not expose a public capability-extension registration
    hook. Its low-level server does build a serializable capabilities object, so
    this adapter wraps that single method and adds the documented Prompt Opinion
    extension without changing transport behavior.
    """

    low_level_server = getattr(mcp_server, "_mcp_server", None)
    if low_level_server is None:
        return False

    marker = "_prompt_opinion_fhir_context_extension_installed"
    if getattr(low_level_server, marker, False):
        return True

    get_capabilities = getattr(low_level_server, "get_capabilities", None)
    if not callable(get_capabilities):
        return False

    @wraps(get_capabilities)
    def get_capabilities_with_fhir_context(*args: Any, **kwargs: Any) -> Any:
        capabilities = get_capabilities(*args, **kwargs)
        return attach_fhir_context_extension(capabilities)

    low_level_server.get_capabilities = get_capabilities_with_fhir_context
    setattr(low_level_server, marker, True)
    return True
