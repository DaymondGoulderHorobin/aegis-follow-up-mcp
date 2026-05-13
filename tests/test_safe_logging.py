from app.safety.logging import (
    OMITTED_VALUE,
    REDACTED_VALUE,
    build_safe_log_event,
    redact_sensitive_log_fields,
)


def test_safe_log_event_redacts_token_like_values() -> None:
    event = build_safe_log_event(
        "fhir_context_checked",
        {
            "status": "not_attempted",
            "access_token": "secret-token",
            "X-FHIR-Access-Token": "another-secret-token",
            "authorization": "Bearer secret-token",
        },
    )

    assert event["event"] == "fhir_context_checked"
    assert event["fields"]["status"] == "not_attempted"
    assert event["fields"]["access_token"] == REDACTED_VALUE
    assert event["fields"]["X-FHIR-Access-Token"] == REDACTED_VALUE
    assert event["fields"]["authorization"] == REDACTED_VALUE
    assert "secret-token" not in str(event)


def test_safe_log_event_omits_payload_shaped_values() -> None:
    fields = redact_sensitive_log_fields(
        {
            "tool_name": "validate_fhir_context_connection",
            "http_status": 200,
            "patient": {"name": "Example Patient"},
            "observations": [{"value": "PHI-shaped data"}],
            "raw_fhir_payload": {"resourceType": "Bundle"},
        }
    )

    assert fields["tool_name"] == "validate_fhir_context_connection"
    assert fields["http_status"] == 200
    assert fields["patient"] == OMITTED_VALUE
    assert fields["observations"] == OMITTED_VALUE
    assert fields["raw_fhir_payload"] == REDACTED_VALUE
    assert "Example Patient" not in str(fields)
