"""Deterministic follow-up task queue service."""

from __future__ import annotations

from typing import Any

from app.fhir.fixtures import iter_resources, load_synthetic_bundle
from app.fhir.models import AbnormalFinding
from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)
from app.services.audit_trail import explain_result_decisions
from app.services.follow_up_priority import _priority_tier
from app.services.patient_snapshot import get_patient_snapshot
from app.services.rule_profiles import DEFAULT_PROFILE_ID, PRIORITY_ORDER, get_rule_profile
from app.services.workflow_state import get_task_status


def list_follow_up_tasks(
    profile_id: str = DEFAULT_PROFILE_ID,
    patient_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Return a priority-grouped demo task queue for unresolved findings."""

    profile = get_rule_profile(profile_id)
    selected_patient_ids = patient_ids or _all_patient_ids()
    tasks = [
        task
        for patient_id in selected_patient_ids
        for task in _tasks_for_patient(patient_id, profile["profile_id"])
    ]
    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "profile_id": profile["profile_id"],
        "generated_from": "synthetic_fixture_data",
        "demo_state_only": True,
        "ehr_write_performed": False,
        "included_patient_ids": selected_patient_ids,
        "task_groups": _group_tasks(tasks),
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload


def _tasks_for_patient(patient_id: str, profile_id: str) -> list[dict[str, Any]]:
    patient = get_patient_snapshot(patient_id=patient_id)
    audit_payload = explain_result_decisions(patient_id=patient_id, profile_id=profile_id)
    tasks: list[dict[str, Any]] = []
    for decision in audit_payload["decisions"]:
        if decision["decision"] != "flagged":
            continue
        priority_tier = _priority_tier_for_decision(decision, profile_id)
        task_id = f"task-{patient_id}-{decision['resource_id']}"
        tasks.append(
            {
                "task_id": task_id,
                "patient_id": patient_id,
                "patient_name": patient.name,
                "finding_display": decision["display"],
                "priority_tier": priority_tier,
                "status": get_task_status(task_id),
                "audit_decision_id": decision["decision_id"],
                "clinician_review_statement": decision["clinician_review_statement"],
            }
        )
    return tasks


def _priority_tier_for_decision(decision: dict[str, Any], profile_id: str) -> str:
    finding = AbnormalFinding(
        observation_id=decision["resource_id"],
        display=decision["display"],
        severity=decision["severity"],
        reason=decision["reason"],
        evidence=decision["evidence"],
        suggested_clinician_review_action=decision["clinician_review_statement"],
    )
    return _priority_tier([finding], profile_id=profile_id)


def _group_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        grouped.setdefault(task["priority_tier"], []).append(task)
    return [
        {"priority_tier": tier, "tasks": grouped[tier]}
        for tier in sorted(grouped, key=lambda item: PRIORITY_ORDER[item])
    ]


def _all_patient_ids() -> list[str]:
    bundle = load_synthetic_bundle()
    return [
        str(patient["id"])
        for patient in iter_resources("Patient", bundle)
        if patient.get("id")
    ]
