"""Smoke-test a running Follow-Up Radar MCP endpoint."""

from __future__ import annotations

import argparse
import asyncio
from typing import Any

from fastmcp import Client

EXPECTED_TOOLS = {
    "get_patient_snapshot",
    "get_recent_observations",
    "find_unresolved_abnormal_results",
    "generate_follow_up_brief",
    "draft_clinician_note",
}


def _content_to_text(result: Any) -> str:
    content = getattr(result, "content", None)
    if not content:
        return str(result)
    return "\n".join(str(getattr(item, "text", item)) for item in content)


async def smoke(url: str) -> None:
    async with Client(url, timeout=20, init_timeout=20) as client:
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
    if "Hemoglobin A1c" not in findings_text or "LDL cholesterol" not in findings_text:
        raise SystemExit("Expected unresolved abnormal findings were not returned.")
    if "Clinical decision support only" not in brief_text:
        raise SystemExit("Follow-up brief did not include the safety disclaimer.")

    print("MCP smoke check passed.")
    print(f"Endpoint: {url}")
    print(f"Tools: {', '.join(sorted(tool_names))}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp/")
    args = parser.parse_args()
    asyncio.run(smoke(args.url))


if __name__ == "__main__":
    main()
