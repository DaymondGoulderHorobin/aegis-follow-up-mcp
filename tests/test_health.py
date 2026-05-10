from fastapi.testclient import TestClient

from app.main import app
from app.mcp_server import get_registered_tool_names

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


def test_healthz() -> None:
    with TestClient(app) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz() -> None:
    with TestClient(app) as client:
        response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"ready": True}


def test_version() -> None:
    with TestClient(app) as client:
        response = client.get("/version")

    assert response.status_code == 200
    assert response.json()["project"] == "Follow-Up Radar MCP"
    assert response.json()["version"] == "0.6.0"
    assert response.json()["mcp_transport"] == "streamable-http"


def test_mcp_endpoint_is_available_and_tools_are_registered() -> None:
    with TestClient(app) as client:
        response = client.get("/mcp")

    assert response.status_code < 500
    assert set(get_registered_tool_names()) == EXPECTED_TOOLS
    if response.status_code == 200 and response.headers.get("content-type") == "application/json":
        assert set(response.json()["tools"]) == EXPECTED_TOOLS
