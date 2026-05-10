"""Prompt Opinion integration helpers."""

from app.prompt_opinion.fhir_context_extension import (
    DEFAULT_FHIR_CONTEXT_SCOPES,
    PROMPT_OPINION_FHIR_CONTEXT_EXTENSION,
    attach_fhir_context_extension,
    build_capabilities_extensions,
    build_fhir_context_extension,
    install_fhir_context_extension,
)

__all__ = [
    "DEFAULT_FHIR_CONTEXT_SCOPES",
    "PROMPT_OPINION_FHIR_CONTEXT_EXTENSION",
    "attach_fhir_context_extension",
    "build_capabilities_extensions",
    "build_fhir_context_extension",
    "install_fhir_context_extension",
]
