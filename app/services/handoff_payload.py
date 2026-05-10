"""Payload-only follow-up handoff construction."""

from __future__ import annotations

from typing import Any

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)
from app.services.audit_trail import explain_result_decisions
from app.services.follow_up_priority import assess_follow_up_priority
from app.services.follow_up_tasks import list_follow_up_tasks
from app.services.rule_profiles import DEFAULT_PROFILE_ID

DEFAULT_HANDOFF_PATIENT_ID = "synthetic-patient-003"


def create_follow_up_handoff_payload(
    patient_id: str | None = DEFAULT_HANDOFF_PATIENT_ID,
    profile_id: str = DEFAULT_PROFILE_ID,
) -> dict[str, Any]:
    """Return a structured handoff payload without sending it anywhere."""

    resolved_patient_id = patient_id or DEFAULT_HANDOFF_PATIENT_ID
    priority = assess_follow_up_priority(
        patient_id=resolved_patient_id,
        profile_id=profile_id,
    )
    audit = explain_result_decisions(
        patient_id=resolved_patient_id,
        profile_id=profile_id,
    )
    tasks = _tasks_for_patient(resolved_patient_id, profile_id)
    task = tasks[0] if tasks else None
    payload = _handoff_payload(
        patient_id=resolved_patient_id,
        profile_id=profile_id,
        priority=priority,
        audit=audit,
        task=task,
    )
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload


def _tasks_for_patient(patient_id: str, profile_id: str) -> list[dict[str, Any]]:
    task_queue = list_follow_up_tasks(profile_id=profile_id, patient_ids=[patient_id])
    return [
        task
        for group in task_queue["task_groups"]
        for task in group["tasks"]
    ]


def _handoff_payload(
    patient_id: str,
    profile_id: str,
    priority: dict[str, Any],
    audit: dict[str, Any],
    task: dict[str, Any] | None,
) -> dict[str, Any]:
    base_payload: dict[str, Any] = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "handoff_type": "follow_up_task",
        "recipient_agent_type": "scheduling_or_care_coordination_agent",
        "patient_id": patient_id,
        "profile_id": profile_id,
        "priority_tier": priority["priority_tier"],
        "required_human_review": True,
        "ehr_write_performed": False,
        "payload_only": True,
        "outbound_action_performed": False,
        "source_tools": [
            "list_follow_up_tasks",
            "assess_follow_up_priority",
            "explain_result_decisions",
        ],
    }
    if task is None:
        return {
            **base_payload,
            "status": "no_handoff_available",
            "task_id": None,
            "finding_display": None,
            "audit_decision_id": None,
            "no_handoff_reason": (
                "No unresolved follow-up task exists for this synthetic patient."
            ),
        }

    return {
        **base_payload,
        "status": "handoff_payload_created",
        "handoff_id": f"handoff-{task['task_id']}",
        "task_id": task["task_id"],
        "finding_display": task["finding_display"],
        "audit_decision_id": task["audit_decision_id"],
        "audit_decision_count": audit["decision_counts"],
        "task_status": task["status"],
    }
