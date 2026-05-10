"""Smoke-test a running Follow-Up Radar MCP endpoint."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from fastmcp import Client

from app.prompt_opinion.fhir_context_extension import (
    DEFAULT_FHIR_CONTEXT_SCOPES,
    PROMPT_OPINION_FHIR_CONTEXT_EXTENSION,
)

EXPECTED_TOOLS = {
    "get_patient_snapshot",
    "get_recent_observations",
    "find_unresolved_abnormal_results",
    "generate_follow_up_brief",
    "draft_clinician_note",
    "assess_follow_up_priority",
    "list_rule_profiles",
    "explain_result_decisions",
    "list_follow_up_tasks",
    "update_follow_up_task_status",
    "get_ehr_integration_summary",
}


def _normalize_mcp_url(url: str) -> str:
    if not url:
        raise SystemExit("A non-empty MCP endpoint URL is required.")
    normalized = url.strip()
    if not normalized.endswith("/"):
        normalized += "/"
    return normalized


def _content_to_text(result: Any) -> str:
    content = getattr(result, "content", None)
    if not content:
        return str(result)
    return "\n".join(str(getattr(item, "text", item)) for item in content)


async def _with_retries(
    operation: Callable[[], Awaitable[None]],
    attempts: int,
    delay_seconds: float,
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            await operation()
            return
        except Exception as exc:  # noqa: BLE001 - smoke script should report any failure.
            last_error = exc
            if attempt == attempts:
                break
            await asyncio.sleep(delay_seconds)
    raise SystemExit(f"MCP smoke check failed after {attempts} attempt(s): {last_error}")


def _require_text(haystack: str, needle: str, label: str) -> None:
    if needle not in haystack:
        raise SystemExit(f"Expected {needle!r} in {label}.")


def _extensions_from_capabilities(capabilities: Any) -> dict[str, Any]:
    extensions = getattr(capabilities, "extensions", None)
    if extensions is None:
        model_extra = getattr(capabilities, "model_extra", None) or {}
        extensions = model_extra.get("extensions", {})
    if not isinstance(extensions, dict):
        return {}
    return extensions


def _validate_prompt_opinion_extension(initialize_result: Any) -> dict[str, Any]:
    capabilities = getattr(initialize_result, "capabilities", None)
    extensions = _extensions_from_capabilities(capabilities)
    extension = extensions.get(PROMPT_OPINION_FHIR_CONTEXT_EXTENSION)
    if extension is None:
        raise SystemExit(
            f"Missing {PROMPT_OPINION_FHIR_CONTEXT_EXTENSION!r} in initialize capabilities."
        )

    scopes = extension.get("scopes", [])
    expected_scope_names = [scope["name"] for scope in DEFAULT_FHIR_CONTEXT_SCOPES]
    actual_scope_names = [scope.get("name") for scope in scopes]
    if actual_scope_names != expected_scope_names:
        raise SystemExit(
            "Prompt Opinion FHIR-context scopes did not match expected optional scopes."
        )
    if any(scope.get("required", False) for scope in scopes):
        raise SystemExit("Prompt Opinion FHIR-context scopes must be optional by default.")
    if "offline_access" in actual_scope_names:
        raise SystemExit("offline_access must not be requested for this demo.")

    return {
        "name": PROMPT_OPINION_FHIR_CONTEXT_EXTENSION,
        "scopes": actual_scope_names,
        "required_scopes": [
            scope.get("name")
            for scope in scopes
            if scope.get("required", False)
        ],
    }


async def smoke_once(url: str, timeout: float) -> dict[str, Any]:
    async with Client(url, timeout=timeout, init_timeout=timeout) as client:
        initialize_result = client.initialize_result or await client.initialize()
        extension_summary = _validate_prompt_opinion_extension(initialize_result)
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools}
        missing = EXPECTED_TOOLS - tool_names
        if missing:
            raise SystemExit(f"Missing expected tools: {sorted(missing)}")

        findings = await client.call_tool(
            "find_unresolved_abnormal_results",
            {"patient_id": "synthetic-patient-001"},
        )
        brief = await client.call_tool(
            "generate_follow_up_brief",
            {"patient_id": "synthetic-patient-001"},
        )
        priority = await client.call_tool(
            "assess_follow_up_priority",
            {"patient_id": "synthetic-patient-003"},
        )
        tasks = await client.call_tool("list_follow_up_tasks", {})
        audit = await client.call_tool(
            "explain_result_decisions",
            {"patient_id": "synthetic-patient-001"},
        )
        workflow_update = await client.call_tool(
            "update_follow_up_task_status",
            {
                "task_id": "task-synthetic-patient-003-obs-potassium-003-2026-04-24",
                "status": "reviewed",
                "reason": "Clinician reviewed during demo workflow.",
            },
        )

    findings_text = _content_to_text(findings)
    brief_text = _content_to_text(brief)
    priority_text = _content_to_text(priority)
    tasks_text = _content_to_text(tasks)
    audit_text = _content_to_text(audit)
    workflow_text = _content_to_text(workflow_update)
    _require_text(findings_text, "Hemoglobin A1c", "unresolved abnormal findings")
    _require_text(findings_text, "LDL cholesterol", "unresolved abnormal findings")
    _require_text(brief_text, "Clinical decision support only", "follow-up brief")
    _require_text(
        priority_text,
        "same_day_clinician_review_consideration",
        "follow-up priority assessment",
    )
    _require_text(tasks_text, "synthetic-patient-003", "follow-up task queue")
    _require_text(
        tasks_text,
        "same_day_clinician_review_consideration",
        "follow-up task queue",
    )
    _require_text(audit_text, "Hemoglobin A1c", "audit trail")
    _require_text(audit_text, "flagged", "audit trail")
    _require_text(workflow_text, "demo_state_only", "workflow update")
    _require_text(workflow_text, "ehr_write_performed", "workflow update")

    return {
        "endpoint": url,
        "tools": sorted(tool_names),
        "prompt_opinion_extension": extension_summary,
        "validated_calls": [
            "initialize_capabilities",
            "find_unresolved_abnormal_results",
            "generate_follow_up_brief",
            "assess_follow_up_priority",
            "list_follow_up_tasks",
            "explain_result_decisions",
            "update_follow_up_task_status",
        ],
    }


async def smoke(url: str, attempts: int, delay_seconds: float, timeout: float) -> None:
    normalized_url = _normalize_mcp_url(url)
    result: dict[str, Any] = {}

    async def run_once() -> None:
        nonlocal result
        result = await smoke_once(normalized_url, timeout)

    await _with_retries(run_once, attempts, delay_seconds)
    print("MCP smoke check passed.")
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp/")
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    asyncio.run(smoke(args.url, args.attempts, args.delay_seconds, args.timeout))


if __name__ == "__main__":
    main()
