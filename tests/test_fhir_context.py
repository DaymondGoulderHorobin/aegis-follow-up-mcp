from app.fhir.context import parse_fhir_context
from app.safety.redaction import redact_headers


def test_missing_fhir_context_uses_fixture_mode() -> None:
    context = parse_fhir_context({})

    assert context.fixture_mode is True
    assert context.has_external_context is False


def test_complete_fhir_context_disables_fixture_mode() -> None:
    context = parse_fhir_context(
        {
            "X-FHIR-Server-URL": "https://example.fhir.test",
            "X-FHIR-Access-Token": "secret-token",
            "X-Patient-ID": "patient-123",
        }
    )

    assert context.fixture_mode is False
    assert context.has_external_context is True
    assert context.patient_id == "patient-123"
    assert "secret-token" not in repr(context)
    assert context.safe_summary()["access_token"] == "[REDACTED]"


def test_token_redaction() -> None:
    redacted = redact_headers(
        {
            "X-FHIR-Access-Token": "secret-token",
            "X-Patient-ID": "patient-123",
        }
    )

    assert redacted["X-FHIR-Access-Token"] == "[REDACTED]"
    assert redacted["X-Patient-ID"] == "patient-123"


def test_patient_id_header_can_drive_fixture_mode_without_external_context() -> None:
    context = parse_fhir_context({"X-Patient-ID": "synthetic-patient-002"})

    assert context.fixture_mode is True
    assert context.patient_id == "synthetic-patient-002"
