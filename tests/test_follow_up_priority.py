from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.services.follow_up_priority import assess_follow_up_priority


def test_critical_potassium_patient_gets_same_day_review_consideration() -> None:
    assessment = assess_follow_up_priority(patient_id="synthetic-patient-003")

    assert assessment["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert assessment["patient_id"] == "synthetic-patient-003"
    assert assessment["profile_id"] == "default_primary_care"
    assert assessment["priority_tier"] == "same_day_clinician_review_consideration"
    assert assessment["findings"][0]["display"] == "Potassium"
    assert assessment["findings"][0]["severity"] == "high"
    assert assessment["suggested_clinician_review_actions"] == [
        "Clinician may wish to review and document follow-up status if appropriate."
    ]


def test_clean_patient_gets_no_unresolved_result_tier() -> None:
    assessment = assess_follow_up_priority(patient_id="synthetic-patient-004")

    assert assessment["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert assessment["priority_tier"] == "no_unresolved_abnormal_result_found"
    assert assessment["findings"] == []
    assert assessment["suggested_clinician_review_actions"] == []


def test_follow_up_evidence_patient_gets_no_unresolved_result_tier() -> None:
    assessment = assess_follow_up_priority(patient_id="synthetic-patient-005")

    assert assessment["priority_tier"] == "no_unresolved_abnormal_result_found"
    assert assessment["findings"] == []


def test_existing_patient_gets_soon_review_consideration() -> None:
    assessment = assess_follow_up_priority(patient_id="synthetic-patient-001")
    finding_displays = {finding["display"] for finding in assessment["findings"]}

    assert assessment["priority_tier"] == "soon_clinician_review_consideration"
    assert finding_displays == {"Hemoglobin A1c", "LDL cholesterol"}
    assert "Potassium" not in finding_displays
