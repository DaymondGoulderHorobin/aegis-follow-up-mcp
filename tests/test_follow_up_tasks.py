from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.services.follow_up_tasks import list_follow_up_tasks
from app.services.workflow_state import reset_demo_workflow_state, update_follow_up_task_status


def test_task_queue_groups_patients_by_priority() -> None:
    reset_demo_workflow_state()
    queue = list_follow_up_tasks()
    groups = {group["priority_tier"]: group["tasks"] for group in queue["task_groups"]}

    assert queue["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert queue["demo_state_only"] is True
    assert queue["ehr_write_performed"] is False
    assert groups["same_day_clinician_review_consideration"][0]["patient_id"] == (
        "synthetic-patient-003"
    )
    soon_patient_ids = {
        task["patient_id"]
        for task in groups["soon_clinician_review_consideration"]
    }
    assert "synthetic-patient-001" in soon_patient_ids


def test_task_queue_omits_clean_chart_patient_from_open_groups() -> None:
    queue = list_follow_up_tasks(patient_ids=["synthetic-patient-004"])

    assert queue["included_patient_ids"] == ["synthetic-patient-004"]
    assert queue["task_groups"] == []


def test_task_queue_reflects_demo_status_update() -> None:
    reset_demo_workflow_state()
    task_id = "task-synthetic-patient-003-obs-potassium-003-2026-04-24"
    update_follow_up_task_status(
        task_id=task_id,
        status="reviewed",
        reason="Clinician reviewed during demo workflow.",
    )

    queue = list_follow_up_tasks(patient_ids=["synthetic-patient-003"])

    assert queue["task_groups"][0]["tasks"][0]["status"] == "reviewed"
