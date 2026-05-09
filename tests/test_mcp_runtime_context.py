import app.fhir.context as fhir_context
from app.mcp_server import get_patient_snapshot


def test_mcp_tool_uses_runtime_patient_id_header(monkeypatch) -> None:
    monkeypatch.setattr(
        fhir_context,
        "get_http_headers",
        lambda: {
            "x-fhir-server-url": "https://example.fhir.test",
            "x-fhir-access-token": "secret-token",
            "x-patient-id": "synthetic-patient-002",
        },
    )

    snapshot = get_patient_snapshot()

    assert snapshot["patient_id"] == "synthetic-patient-002"
    assert snapshot["name"] == "Jamie Ngata"
