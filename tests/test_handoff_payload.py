import pytest

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.services.handoff_payload import create_follow_up_handoff_payload


def test_handoff_payload_uses_existing_priority_task_and_audit_context() -> None:
    payload = create_follow_up_handoff_payload(patient_id="synthetic-patient-003")

    assert payload["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert payload["status"] == "handoff_payload_created"
    assert payload["handoff_type"] == "follow_up_task"
    assert payload["recipient_agent_type"] == "scheduling_or_care_coordination_agent"
    assert payload["patient_id"] == "synthetic-patient-003"
    assert payload["priority_tier"] == "same_day_clinician_review_consideration"
    assert payload["finding_display"] == "Potassium"
    assert payload["task_id"].startswith("task-synthetic-patient-003-obs-potassium")
    assert payload["audit_decision_id"].startswith("audit-synthetic-patient-003")
    assert payload["required_human_review"] is True
    assert payload["ehr_write_performed"] is False
    assert payload["payload_only"] is True
    assert payload["outbound_action_performed"] is False


def test_handoff_payload_does_not_invent_task_for_clean_patient() -> None:
    payload = create_follow_up_handoff_payload(patient_id="synthetic-patient-004")

    assert payload["status"] == "no_handoff_available"
    assert payload["priority_tier"] == "no_unresolved_abnormal_result_found"
    assert payload["task_id"] is None
    assert payload["finding_display"] is None
    assert payload["audit_decision_id"] is None
    assert payload["required_human_review"] is True
    assert payload["ehr_write_performed"] is False
    assert payload["payload_only"] is True


def test_handoff_payload_rejects_invalid_profile_clearly() -> None:
    with pytest.raises(ValueError, match="Unknown rule profile"):
        create_follow_up_handoff_payload(
            patient_id="synthetic-patient-003",
            profile_id="not-a-profile",
        )
