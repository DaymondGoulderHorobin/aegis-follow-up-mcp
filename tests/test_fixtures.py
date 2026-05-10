from app.fhir.fixtures import first_resource, iter_resources, load_synthetic_bundle
from app.services.observations import get_recent_observations


def test_fixture_bundle_loads_synthetic_patient() -> None:
    bundle = load_synthetic_bundle()
    patient = first_resource("Patient", bundle)

    assert bundle["resourceType"] == "Bundle"
    assert patient["id"] == "synthetic-patient-001"
    assert patient["name"][0]["family"] == "Rivera"


def test_fixture_has_recent_observations_with_abnormal_examples() -> None:
    observations = get_recent_observations()
    abnormal = [observation for observation in observations if observation.abnormal]

    assert len(observations) >= 5
    assert len(abnormal) >= 2


def test_fixture_contains_multi_patient_sprint_five_scenarios() -> None:
    bundle = load_synthetic_bundle()
    patient_ids = {patient["id"] for patient in iter_resources("Patient", bundle)}

    assert {
        "synthetic-patient-001",
        "synthetic-patient-003",
        "synthetic-patient-004",
        "synthetic-patient-005",
    }.issubset(patient_ids)
