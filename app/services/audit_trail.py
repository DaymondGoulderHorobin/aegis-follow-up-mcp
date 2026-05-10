"""Structured audit trail for deterministic result decisions."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.fhir.fixtures import default_patient_id, iter_resources, load_synthetic_bundle
from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)
from app.services.abnormal_results import (
    FOLLOW_UP_RESOURCE_TYPES,
    _reference_text,
    _severity_for_observation,
)
from app.services.observations import get_recent_observations
from app.services.rule_profiles import DEFAULT_PROFILE_ID, get_rule_profile

FLAGGED_RULE_ID = "abnormal-no-follow-up-v1"
SUPPRESSED_RULE_ID = "abnormal-follow-up-evidence-v1"


def explain_result_decisions(
    patient_id: str | None = None,
    profile_id: str = DEFAULT_PROFILE_ID,
) -> dict[str, Any]:
    """Return deterministic audit decisions for flagged and suppressed observations."""

    source_bundle = load_synthetic_bundle()
    requested_patient_id = patient_id or default_patient_id(source_bundle)
    profile = get_rule_profile(profile_id)
    decisions = [
        decision
        for observation in get_recent_observations(
            patient_id=requested_patient_id,
            bundle=source_bundle,
        )
        for decision in [
            _audit_decision_for_observation(
                patient_id=requested_patient_id or "synthetic-patient",
                observation=observation.model_dump(),
                source_bundle=source_bundle,
                profile=profile,
            )
        ]
        if decision is not None
    ]
    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "patient_id": requested_patient_id,
        "profile_id": profile["profile_id"],
        "generated_from": "synthetic_fixture_data",
        "included_decisions": ["flagged", "suppressed"],
        "decision_counts": _decision_counts(decisions),
        "decisions": decisions,
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload


def _audit_decision_for_observation(
    patient_id: str,
    observation: dict[str, Any],
    source_bundle: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any] | None:
    if not observation["abnormal"]:
        return None

    follow_up = _follow_up_resource_for_observation(
        observation["id"],
        observation["effective_date"],
        source_bundle,
    )
    if follow_up is not None:
        return _decision_payload(
            patient_id=patient_id,
            observation=observation,
            decision="suppressed",
            rule_id=SUPPRESSED_RULE_ID,
            profile=profile,
            reason="Observation is abnormal and follow-up evidence was found.",
            suppression_reason=_suppression_reason(follow_up),
        )

    return _decision_payload(
        patient_id=patient_id,
        observation=observation,
        decision="flagged",
        rule_id=FLAGGED_RULE_ID,
        profile=profile,
        reason="Observation is abnormal and no follow-up evidence was found.",
        suppression_reason=None,
    )


def _decision_payload(
    patient_id: str,
    observation: dict[str, Any],
    decision: str,
    rule_id: str,
    profile: dict[str, Any],
    reason: str,
    suppression_reason: str | None,
) -> dict[str, Any]:
    severity = _severity_for_observation(
        observation["value"],
        observation["reference_low"],
        observation["reference_high"],
        observation["interpretation"],
    )
    return {
        "decision_id": f"audit-{patient_id}-{observation['id']}",
        "patient_id": patient_id,
        "resource_type": "Observation",
        "resource_id": observation["id"],
        "display": observation["display"],
        "decision": decision,
        "severity": severity,
        "rule_id": rule_id,
        "profile_id": profile["profile_id"],
        "reason": reason,
        "evidence": [
            f"{observation['display']}: {observation['value']:g} {observation['unit']}",
            f"Effective date: {observation['effective_date']}",
            _reference_text(observation["reference_low"], observation["reference_high"]),
        ],
        "suppression_reason": suppression_reason,
        "clinician_review_statement": profile["safety_language"],
    }


def _decision_counts(decisions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "flagged": sum(1 for decision in decisions if decision["decision"] == "flagged"),
        "suppressed": sum(1 for decision in decisions if decision["decision"] == "suppressed"),
    }


def _follow_up_resource_for_observation(
    observation_id: str,
    observation_date: str,
    bundle: dict[str, Any],
) -> dict[str, Any] | None:
    observed_at = _safe_parse_date(observation_date)
    if observed_at is None:
        return None
    for resource in iter_resources(bundle=bundle):
        if resource.get("resourceType") not in FOLLOW_UP_RESOURCE_TYPES:
            continue
        if f"Observation/{observation_id}" not in _extract_references(resource):
            continue
        follow_up_date = _resource_date(resource)
        if follow_up_date is None or follow_up_date >= observed_at:
            return resource
    return None


def _suppression_reason(resource: dict[str, Any]) -> str:
    resource_type = resource.get("resourceType", "Resource")
    resource_id = resource.get("id", "unknown")
    date_text = _resource_date_text(resource) or "unknown date"
    return (
        f"Suppressed because {resource_type}/{resource_id} references this observation "
        f"with follow-up date {date_text}."
    )


def _extract_references(value: Any) -> set[str]:
    references: set[str] = set()
    if isinstance(value, dict):
        reference = value.get("reference")
        if isinstance(reference, str):
            references.add(reference)
        for child in value.values():
            references.update(_extract_references(child))
    elif isinstance(value, list):
        for item in value:
            references.update(_extract_references(item))
    return references


def _resource_date(resource: dict[str, Any]) -> datetime | None:
    return _safe_parse_date(_resource_date_text(resource))


def _resource_date_text(resource: dict[str, Any]) -> str | None:
    period = resource.get("period")
    period_start = period.get("start") if isinstance(period, dict) else None
    for value in (
        resource.get("authoredOn"),
        resource.get("occurrenceDateTime"),
        resource.get("effectiveDateTime"),
        resource.get("issued"),
        resource.get("created"),
        resource.get("performedDateTime"),
        period_start,
    ):
        if isinstance(value, str) and value:
            return value
    return None


def _safe_parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
