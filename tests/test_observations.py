from app.services.observations import get_recent_observations


def test_patient_observations_are_filtered_by_selected_patient() -> None:
    observations = get_recent_observations(patient_id="synthetic-patient-002")
    displays = {observation.display for observation in observations}

    assert displays == {"Systolic blood pressure", "Diastolic blood pressure"}
    assert all(not observation.abnormal for observation in observations)


def test_malformed_observations_are_skipped_without_crashing() -> None:
    bundle = {
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-edge",
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-missing-value",
                    "subject": {"reference": "Patient/patient-edge"},
                    "effectiveDateTime": "2026-04-01T00:00:00+12:00",
                    "code": {"text": "Missing value"},
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-nonnumeric",
                    "subject": {"reference": "Patient/patient-edge"},
                    "effectiveDateTime": "2026-04-01T00:00:00+12:00",
                    "code": {"text": "Non-numeric value"},
                    "valueQuantity": {"value": "not-a-number", "unit": "mg/dL"},
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-valid",
                    "subject": {"reference": "Patient/patient-edge"},
                    "effectiveDateTime": "2026-04-01T00:00:00+12:00",
                    "code": {"text": "Valid value"},
                    "valueQuantity": {"value": 7.1, "unit": "mg/dL"},
                }
            },
        ]
    }

    observations = get_recent_observations(patient_id="patient-edge", bundle=bundle)

    assert [observation.id for observation in observations] == ["obs-valid"]
