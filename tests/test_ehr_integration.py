from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import find_disallowed_clinical_phrases
from app.services.ehr_integration import get_ehr_integration_summary


def test_ehr_integration_summary_is_safe_and_honest() -> None:
    summary = get_ehr_integration_summary()

    assert summary["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert summary["current_demo_mode"] == "FHIR context and synthetic fixture read path only."
    assert "Observation" in summary["input_resources"]
    assert "task queue" in summary["current_outputs"]
    assert summary["demo_state_only"] is True
    assert summary["ehr_write_performed"] is False
    assert "No autonomous EHR write" in summary["safety_boundary"]
    assert find_disallowed_clinical_phrases(str(summary)) == []
