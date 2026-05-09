from app.fhir.fixtures import first_resource, load_synthetic_bundle
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
