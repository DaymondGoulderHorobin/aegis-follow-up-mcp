import httpx

from app.services.fhir_connectivity import validate_fhir_context_connection

FHIR_HEADERS = {
    "X-FHIR-Server-URL": "https://example.fhir.test",
    "X-FHIR-Access-Token": "secret-token",
    "X-Patient-ID": "patient-123",
}


def _client_factory(handler):
    def factory(**kwargs):
        return httpx.Client(transport=httpx.MockTransport(handler), **kwargs)

    return factory


def test_missing_fhir_context_returns_not_attempted() -> None:
    result = validate_fhir_context_connection(
        headers={},
        live_fhir_reads_enabled=True,
    )

    assert result["status"] == "not_attempted"
    assert result["reason"] == "missing_fhir_context"
    assert result["server_url_present"] is False
    assert result["access_token_present"] is False
    assert result["patient_id_present"] is False
    assert result["live_fhir_reads_enabled"] is False
    assert result["request_attempted"] is False
    assert result["token_disclosed"] is False
    assert result["payload_includes_phi"] is False


def test_context_present_but_live_reads_disabled_returns_not_attempted() -> None:
    def fail_if_called(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"Unexpected FHIR request: {request.url}")

    result = validate_fhir_context_connection(
        headers=FHIR_HEADERS,
        live_fhir_reads_enabled=False,
        client_factory=_client_factory(fail_if_called),
    )

    assert result["status"] == "not_attempted"
    assert result["reason"] == "live_fhir_reads_disabled"
    assert result["server_url_present"] is True
    assert result["access_token_present"] is True
    assert result["patient_id_present"] is True
    assert result["live_fhir_reads_enabled"] is False
    assert result["request_attempted"] is False


def test_successful_patient_lookup_returns_safe_reachable_metadata() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://example.fhir.test/Patient/patient-123"
        assert request.headers["Authorization"] == "Bearer secret-token"
        return httpx.Response(
            200,
            json={
                "resourceType": "Patient",
                "id": "patient-123",
                "name": [{"family": "Example"}],
                "telecom": [{"value": "555-0100"}],
            },
        )

    result = validate_fhir_context_connection(
        headers=FHIR_HEADERS,
        live_fhir_reads_enabled=True,
        client_factory=_client_factory(handler),
    )

    assert result["status"] == "reachable"
    assert result["request_attempted"] is True
    assert result["resource_requested"] == "Patient/{patient_id}"
    assert result["http_status"] == 200
    assert result["resource_type"] == "Patient"
    assert result["patient_id_confirmed"] is True
    assert result["clinical_workflow_source"] == "synthetic_fixture_data"
    assert "secret-token" not in str(result)
    assert "patient-123" not in str(result)
    assert "Example" not in str(result)
    assert "555-0100" not in str(result)


def test_authorization_failure_returns_safe_error_metadata() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"issue": "token expired"})

    result = validate_fhir_context_connection(
        headers=FHIR_HEADERS,
        live_fhir_reads_enabled=True,
        client_factory=_client_factory(handler),
    )

    assert result["status"] == "unreachable"
    assert result["request_attempted"] is True
    assert result["http_status"] == 401
    assert result["error_type"] == "authorization_failed"
    assert "secret-token" not in str(result)
    assert "token expired" not in str(result)


def test_forbidden_failure_maps_to_authorization_failed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"issue": "insufficient scope"})

    result = validate_fhir_context_connection(
        headers=FHIR_HEADERS,
        live_fhir_reads_enabled=True,
        client_factory=_client_factory(handler),
    )

    assert result["status"] == "unreachable"
    assert result["http_status"] == 403
    assert result["error_type"] == "authorization_failed"
    assert "insufficient scope" not in str(result)


def test_patient_not_found_returns_safe_error_metadata() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"issue": "not found"})

    result = validate_fhir_context_connection(
        headers=FHIR_HEADERS,
        live_fhir_reads_enabled=True,
        client_factory=_client_factory(handler),
    )

    assert result["status"] == "unreachable"
    assert result["http_status"] == 404
    assert result["error_type"] == "patient_not_found"
    assert "not found" not in str(result)


def test_network_timeout_returns_unreachable_without_token_disclosure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("connection timed out")

    result = validate_fhir_context_connection(
        headers=FHIR_HEADERS,
        live_fhir_reads_enabled=True,
        client_factory=_client_factory(handler),
    )

    assert result["status"] == "unreachable"
    assert result["request_attempted"] is True
    assert result["error_type"] == "timeout"
    assert "secret-token" not in str(result)
    assert "connection timed out" not in str(result)
