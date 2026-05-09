from app.services.patient_snapshot import get_patient_snapshot


def test_patient_lookup_by_id_selects_second_synthetic_patient() -> None:
    snapshot = get_patient_snapshot(patient_id="synthetic-patient-002")

    assert snapshot.patient_id == "synthetic-patient-002"
    assert snapshot.name == "Jamie Ngata"
    assert snapshot.conditions == ["Hypertension"]
    assert snapshot.medications == ["Amlodipine 5 mg tablet"]
    assert snapshot.recent_encounters == [
        "Nurse blood pressure review on 2026-04-18T14:00:00+12:00"
    ]


def test_unknown_patient_id_does_not_fall_back_to_first_patient() -> None:
    snapshot = get_patient_snapshot(patient_id="unknown-patient")

    assert snapshot.patient_id == "unknown-patient"
    assert snapshot.name == "Synthetic Patient"
    assert snapshot.conditions == []
