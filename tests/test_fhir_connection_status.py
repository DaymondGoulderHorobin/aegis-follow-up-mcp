import app.services.fhir_connection_status as fhir_status
from app.config import Settings
from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.services.fhir_connection_status import get_fhir_connection_status


def test_fhir_connection_status_is_fixture_first_without_headers() -> None:
    status = get_fhir_connection_status()

    assert status["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert status["fixture_mode"] is True
    assert status["fhir_context_received"] is False
    assert status["server_url_present"] is False
    assert status["access_token_present"] is False
    assert status["patient_id_present"] is False
    assert status["live_fhir_reads_enabled"] is False
    assert status["live_fhir_connectivity_check_supported"] is False
    assert status["connectivity_proof_tool"] == "validate_fhir_context_connection"
    assert status["connectivity_proof_can_attempt"] is False
    assert status["active_data_source"] == "synthetic_fixture_data"


def test_fhir_connection_status_reports_explicit_patient_without_live_read() -> None:
    status = get_fhir_connection_status(patient_id="synthetic-patient-001")

    assert status["patient_id_present"] is True
    assert status["patient_id_source"] == "explicit_tool_argument"
    assert status["active_data_source"] == "synthetic_fixture_data"


def test_fhir_connection_status_reports_header_presence_without_token_leakage() -> None:
    status = get_fhir_connection_status(
        headers={
            "X-FHIR-Server-URL": "https://example.fhir.test",
            "X-FHIR-Access-Token": "secret-token",
            "X-Patient-ID": "synthetic-patient-001",
        }
    )

    assert status["fhir_context_received"] is True
    assert status["server_url_present"] is True
    assert status["access_token_present"] is True
    assert status["patient_id_present"] is True
    assert status["patient_id_source"] == "fhir_context_header"
    assert status["live_fhir_reads_enabled"] is False
    assert status["connectivity_proof_can_attempt"] is False
    assert status["active_data_source"] == "synthetic_fixture_data"
    assert "secret-token" not in str(status)


def test_fhir_connection_status_keeps_clinical_workflow_synthetic_when_proof_enabled(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        fhir_status,
        "settings",
        Settings(live_fhir_reads_enabled=True),
    )

    status = fhir_status.get_fhir_connection_status(
        headers={
            "X-FHIR-Server-URL": "https://example.fhir.test",
            "X-FHIR-Access-Token": "secret-token",
            "X-Patient-ID": "patient-123",
        }
    )

    assert status["live_fhir_reads_enabled"] is True
    assert status["connectivity_proof_can_attempt"] is True
    assert status["active_data_source"] == "synthetic_fixture_data"
    assert status["clinical_workflow_source"] == "synthetic_fixture_data"
    assert "secret-token" not in str(status)
