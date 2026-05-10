import asyncio
from typing import Any

from fastmcp import Client
from mcp.types import ServerCapabilities

from app.mcp_server import mcp
from app.prompt_opinion.fhir_context_extension import (
    DEFAULT_FHIR_CONTEXT_SCOPES,
    PROMPT_OPINION_FHIR_CONTEXT_EXTENSION,
    attach_fhir_context_extension,
    build_capabilities_extensions,
    build_fhir_context_extension,
)

EXPECTED_SCOPE_NAMES = [
    "patient/Patient.rs",
    "patient/Observation.rs",
    "patient/Condition.rs",
    "patient/MedicationStatement.rs",
    "patient/Encounter.rs",
]


def _extensions_from_capabilities(capabilities: Any) -> dict[str, Any]:
    extensions = getattr(capabilities, "extensions", None)
    if extensions is None:
        model_extra = getattr(capabilities, "model_extra", None) or {}
        extensions = model_extra.get("extensions", {})
    return extensions or {}


def test_extension_payload_contains_prompt_opinion_name() -> None:
    extensions = build_capabilities_extensions()

    assert PROMPT_OPINION_FHIR_CONTEXT_EXTENSION in extensions


def test_extension_payload_contains_only_approved_optional_scopes() -> None:
    extension = build_fhir_context_extension()
    scopes = extension["scopes"]

    assert [scope["name"] for scope in scopes] == EXPECTED_SCOPE_NAMES
    assert scopes == DEFAULT_FHIR_CONTEXT_SCOPES
    assert all(scope["required"] is False for scope in scopes)
    assert "offline_access" not in {scope["name"] for scope in scopes}


def test_extension_payload_is_not_shared_mutable_state() -> None:
    first = build_fhir_context_extension()
    second = build_fhir_context_extension()

    first["scopes"][0]["required"] = True

    assert second["scopes"][0]["required"] is False


def test_capabilities_adapter_preserves_existing_extensions() -> None:
    capabilities = ServerCapabilities()
    capabilities.extensions = {"io.modelcontextprotocol/ui": {}}

    attach_fhir_context_extension(capabilities)

    extensions = _extensions_from_capabilities(capabilities)
    assert "io.modelcontextprotocol/ui" in extensions
    assert PROMPT_OPINION_FHIR_CONTEXT_EXTENSION in extensions


def test_fastmcp_initialize_advertises_prompt_opinion_extension() -> None:
    async def initialize_capabilities() -> Any:
        async with Client(mcp) as client:
            initialize_result = client.initialize_result or await client.initialize()
            return initialize_result.capabilities

    capabilities = asyncio.run(initialize_capabilities())
    extensions = _extensions_from_capabilities(capabilities)

    assert PROMPT_OPINION_FHIR_CONTEXT_EXTENSION in extensions
    assert extensions[PROMPT_OPINION_FHIR_CONTEXT_EXTENSION] == build_fhir_context_extension()
