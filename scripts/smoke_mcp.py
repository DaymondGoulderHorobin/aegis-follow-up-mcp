"""Smoke-test a running Follow-Up Radar MCP endpoint."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from fastmcp import Client

EXPECTED_TOOLS = {
    "get_patient_snapshot",
    "get_recent_observations",
    "find_unresolved_abnormal_results",
    "generate_follow_up_brief",
    "draft_clinician_note",
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


async def smoke_once(url: str, timeout: float) -> dict[str, Any]:
    async with Client(url, timeout=timeout, init_timeout=timeout) as client:
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

    findings_text = _content_to_text(findings)
    brief_text = _content_to_text(brief)
    _require_text(findings_text, "Hemoglobin A1c", "unresolved abnormal findings")
    _require_text(findings_text, "LDL cholesterol", "unresolved abnormal findings")
    _require_text(brief_text, "Clinical decision support only", "follow-up brief")

    return {
        "endpoint": url,
        "tools": sorted(tool_names),
        "validated_calls": [
            "find_unresolved_abnormal_results",
            "generate_follow_up_brief",
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
