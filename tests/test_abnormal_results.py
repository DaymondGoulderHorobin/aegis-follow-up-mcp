from app.services.abnormal_results import find_unresolved_abnormal_results


def test_abnormal_results_find_unresolved_items() -> None:
    findings = find_unresolved_abnormal_results()
    displays = {finding.display for finding in findings}

    assert "Hemoglobin A1c" in displays
    assert "LDL cholesterol" in displays
    assert "Potassium" not in displays
    assert all(finding.evidence for finding in findings)
    assert all(finding.suggested_clinician_review_action for finding in findings)


def test_second_patient_has_no_unresolved_abnormal_results() -> None:
    assert find_unresolved_abnormal_results(patient_id="synthetic-patient-002") == []


def test_resolved_abnormal_result_is_suppressed_with_follow_up_reference() -> None:
    findings = find_unresolved_abnormal_results()

    assert all(finding.observation_id != "obs-potassium-2026-04-21" for finding in findings)
