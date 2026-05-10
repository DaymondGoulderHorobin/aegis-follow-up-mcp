"""In-memory demo workflow state for clinician confirmation flows."""

from __future__ import annotations

from typing import Any

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)

ALLOWED_WORKFLOW_STATUSES = {"reviewed", "follow_up_documented", "dismissed"}
_DEMO_TASK_STATE: dict[str, dict[str, str | None]] = {}


def get_task_status(task_id: str) -> str:
    """Return demo task status, defaulting to open."""

    return str(_DEMO_TASK_STATE.get(task_id, {}).get("status") or "open")


def update_follow_up_task_status(
    task_id: str,
    status: str,
    reason: str | None = None,
) -> dict[str, Any]:
    """Simulate a clinician workflow state update without EHR writes."""

    if status not in ALLOWED_WORKFLOW_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_WORKFLOW_STATUSES))
        raise ValueError(f"Unsupported workflow status {status!r}. Allowed statuses: {allowed}.")
    if status == "dismissed" and not reason:
        raise ValueError("A reason is required when dismissing a demo follow-up task.")

    _DEMO_TASK_STATE[task_id] = {"status": status, "reason": reason}
    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "task_id": task_id,
        "status": status,
        "reason": reason,
        "demo_state_only": True,
        "ehr_write_performed": False,
        "message": "Demo workflow state updated. No EHR write was performed.",
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload


def reset_demo_workflow_state() -> None:
    """Clear in-memory demo state for tests."""

    _DEMO_TASK_STATE.clear()
