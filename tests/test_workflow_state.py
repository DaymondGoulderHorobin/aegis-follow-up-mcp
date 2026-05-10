import pytest

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.services.workflow_state import (
    reset_demo_workflow_state,
    update_follow_up_task_status,
)


def test_workflow_status_update_accepts_reviewed() -> None:
    reset_demo_workflow_state()
    result = update_follow_up_task_status(
        task_id="task-synthetic-patient-003-obs-potassium-003-2026-04-24",
        status="reviewed",
        reason="Clinician reviewed during demo workflow.",
    )

    assert result["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert result["status"] == "reviewed"
    assert result["demo_state_only"] is True
    assert result["ehr_write_performed"] is False


def test_workflow_status_update_accepts_follow_up_documented() -> None:
    reset_demo_workflow_state()
    result = update_follow_up_task_status(
        task_id="task-synthetic-patient-001-obs-a1c-2026-04-20",
        status="follow_up_documented",
        reason="Demo review notes recorded.",
    )

    assert result["status"] == "follow_up_documented"
    assert result["ehr_write_performed"] is False


def test_workflow_status_update_requires_dismissed_reason() -> None:
    reset_demo_workflow_state()

    with pytest.raises(ValueError, match="reason is required"):
        update_follow_up_task_status(
            task_id="task-synthetic-patient-001-obs-ldl-2026-04-20",
            status="dismissed",
        )


def test_workflow_status_update_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="Unsupported workflow status"):
        update_follow_up_task_status(
            task_id="task-synthetic-patient-001-obs-ldl-2026-04-20",
            status="closed",
            reason="Demo only.",
        )
