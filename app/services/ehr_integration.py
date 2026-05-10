"""EHR integration story for the workflow-layer demo."""

from __future__ import annotations

from typing import Any

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)
from app.services.follow_up_tasks import list_follow_up_tasks
from app.services.rule_profiles import DEFAULT_PROFILE_ID, PRIORITY_ORDER
from app.services.workflow_state import ALLOWED_WORKFLOW_STATUSES


def get_ehr_integration_summary() -> dict[str, Any]:
    """Return the current and future EHR integration story."""

    workflow_metrics = _workflow_metrics()
    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "current_demo_mode": "FHIR context and synthetic fixture read path only.",
        "input_resources": [
            "Patient",
            "Observation",
            "Condition",
            "MedicationStatement",
            "Encounter",
        ],
        "current_outputs": [
            "follow-up brief",
            "priority assessment",
            "task queue",
            "audit trail",
            "demo workflow state",
        ],
        "future_ehr_write_targets": [
            "Task",
            "CommunicationRequest",
            "DocumentReference",
            "clinician-reviewed note draft",
        ],
        "integration_flow": (
            "FHIR context in -> deterministic follow-up review -> clinician-reviewed "
            "task or note out."
        ),
        "safety_boundary": (
            "No autonomous EHR write is performed. Clinician review is required."
        ),
        "workflow_metrics": workflow_metrics,
        "demo_state_only": True,
        "ehr_write_performed": False,
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload


def _workflow_metrics() -> dict[str, Any]:
    task_queue = list_follow_up_tasks(profile_id=DEFAULT_PROFILE_ID)
    priority_counts = {tier: 0 for tier in PRIORITY_ORDER}
    status_counts = {"open": 0, **{status: 0 for status in sorted(ALLOWED_WORKFLOW_STATUSES)}}
    total_tasks = 0
    for group in task_queue["task_groups"]:
        tasks = group["tasks"]
        priority_counts[group["priority_tier"]] = len(tasks)
        total_tasks += len(tasks)
        for task in tasks:
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "profile_id": DEFAULT_PROFILE_ID,
        "total_tasks": total_tasks,
        "task_counts_by_priority": priority_counts,
        "demo_status_counts": status_counts,
    }
