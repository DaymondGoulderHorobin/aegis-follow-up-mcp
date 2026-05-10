from app.services.abnormal_results import find_unresolved_abnormal_results
from app.services.handoff_payload import create_follow_up_handoff_payload
from app.services.observations import get_recent_observations
from app.services.patient_snapshot import get_patient_snapshot


def test_unknown_patient_id_stays_empty_without_default_patient_leakage() -> None:
    patient = get_patient_snapshot(patient_id="unknown-patient")
    findings = find_unresolved_abnormal_results(patient_id="unknown-patient")
    handoff = create_follow_up_handoff_payload(patient_id="unknown-patient")

    assert patient.patient_id == "unknown-patient"
    assert patient.conditions == []
    assert findings == []
    assert handoff["status"] == "no_handoff_available"
    assert handoff["patient_id"] == "unknown-patient"


def test_abnormal_observation_without_reference_range_is_reported_safely() -> None:
    bundle = _edge_bundle(
        [
            {
                "resourceType": "Observation",
                "id": "obs-no-reference-range",
                "subject": {"reference": "Patient/patient-edge"},
                "effectiveDateTime": "2026-04-01T00:00:00+12:00",
                "code": {"text": "No reference range marker"},
                "valueQuantity": {"value": 9.2, "unit": "mmol/L"},
                "interpretation": [{"coding": [{"code": "H"}]}],
            }
        ]
    )

    findings = find_unresolved_abnormal_results(patient_id="patient-edge", bundle=bundle)

    assert len(findings) == 1
    assert findings[0].display == "No reference range marker"
    assert "Reference range: not provided" in findings[0].evidence


def test_malformed_observation_date_does_not_crash_follow_up_detection() -> None:
    bundle = _edge_bundle(
        [
            {
                "resourceType": "Observation",
                "id": "obs-malformed-date",
                "subject": {"reference": "Patient/patient-edge"},
                "effectiveDateTime": "not-a-date",
                "code": {"text": "Malformed date marker"},
                "valueQuantity": {"value": 9.2, "unit": "mmol/L"},
                "interpretation": [{"coding": [{"code": "H"}]}],
            },
            {
                "resourceType": "ServiceRequest",
                "id": "service-malformed-date-follow-up",
                "subject": {"reference": "Patient/patient-edge"},
                "reasonReference": [{"reference": "Observation/obs-malformed-date"}],
                "authoredOn": "2026-04-02T00:00:00+12:00",
            },
        ]
    )

    findings = find_unresolved_abnormal_results(patient_id="patient-edge", bundle=bundle)

    assert [finding.observation_id for finding in findings] == ["obs-malformed-date"]


def test_follow_up_reference_without_date_is_handled_consistently() -> None:
    bundle = _edge_bundle(
        [
            {
                "resourceType": "Observation",
                "id": "obs-undated-follow-up",
                "subject": {"reference": "Patient/patient-edge"},
                "effectiveDateTime": "2026-04-01T00:00:00+12:00",
                "code": {"text": "Undated follow-up marker"},
                "valueQuantity": {"value": 9.2, "unit": "mmol/L"},
                "interpretation": [{"coding": [{"code": "H"}]}],
            },
            {
                "resourceType": "ServiceRequest",
                "id": "service-undated-follow-up",
                "subject": {"reference": "Patient/patient-edge"},
                "reasonReference": [{"reference": "Observation/obs-undated-follow-up"}],
            },
        ]
    )

    findings = find_unresolved_abnormal_results(patient_id="patient-edge", bundle=bundle)

    assert findings == []


def test_observation_missing_value_quantity_is_skipped_safely() -> None:
    bundle = _edge_bundle(
        [
            {
                "resourceType": "Observation",
                "id": "obs-missing-value-quantity",
                "subject": {"reference": "Patient/patient-edge"},
                "effectiveDateTime": "2026-04-01T00:00:00+12:00",
                "code": {"text": "Missing value quantity"},
            }
        ]
    )

    assert get_recent_observations(patient_id="patient-edge", bundle=bundle) == []


def _edge_bundle(resources: list[dict[str, object]]) -> dict[str, object]:
    return {
        "resourceType": "Bundle",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-edge",
                    "name": [{"given": ["Edge"], "family": "Patient"}],
                }
            },
            *[{"resource": resource} for resource in resources],
        ],
    }
