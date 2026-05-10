from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import find_disallowed_clinical_phrases
from app.services.ehr_integration import get_ehr_integration_summary
from app.services.workflow_state import (
    reset_demo_workflow_state,
    update_follow_up_task_status,
)


def test_ehr_integration_summary_is_safe_and_honest() -> None:
    summary = get_ehr_integration_summary()

    assert summary["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert summary["current_demo_mode"] == "FHIR context and synthetic fixture read path only."
    assert "Observation" in summary["input_resources"]
    assert "task queue" in summary["current_outputs"]
    assert summary["demo_state_only"] is True
    assert summary["ehr_write_performed"] is False
    assert "No autonomous EHR write" in summary["safety_boundary"]
    assert summary["workflow_metrics"]["total_tasks"] >= 1
    assert (
        summary["workflow_metrics"]["task_counts_by_priority"][
            "same_day_clinician_review_consideration"
        ]
        == 1
    )
    assert find_disallowed_clinical_phrases(str(summary)) == []


def test_ehr_integration_summary_includes_dynamic_workflow_status_counts() -> None:
    reset_demo_workflow_state()
    update_follow_up_task_status(
        task_id="task-synthetic-patient-003-obs-potassium-003-2026-04-24",
        status="reviewed",
        reason="Clinician reviewed during demo workflow.",
    )

    summary = get_ehr_integration_summary()

    assert summary["workflow_metrics"]["demo_status_counts"]["reviewed"] == 1
    assert summary["workflow_metrics"]["demo_status_counts"]["open"] >= 1
