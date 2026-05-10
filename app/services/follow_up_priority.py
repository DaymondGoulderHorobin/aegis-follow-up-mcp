"""Deterministic follow-up priority assessment."""

from __future__ import annotations

from typing import Any, Literal

from app.fhir.models import AbnormalFinding
from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)
from app.services.abnormal_results import find_unresolved_abnormal_results
from app.services.patient_snapshot import get_patient_snapshot
from app.services.rule_profiles import (
    DEFAULT_PROFILE_ID,
    get_rule_profile,
    highest_priority,
    priority_override_for_display,
)

PriorityTier = Literal[
    "same_day_clinician_review_consideration",
    "soon_clinician_review_consideration",
    "routine_clinician_review",
    "no_unresolved_abnormal_result_found",
]

NEUTRAL_REVIEW_ACTION = (
    "Clinician may wish to review the result, confirm follow-up status, "
    "and document the plan if appropriate."
)


def assess_follow_up_priority(
    patient_id: str | None = None,
    profile_id: str = DEFAULT_PROFILE_ID,
) -> dict[str, Any]:
    """Assess deterministic clinician-review priority for unresolved abnormal results."""

    profile = get_rule_profile(profile_id)
    patient = get_patient_snapshot(patient_id=patient_id)
    findings = find_unresolved_abnormal_results(patient_id=patient.patient_id)
    priority_tier = _priority_tier(findings, profile_id=profile["profile_id"])
    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "patient_id": patient.patient_id,
        "profile_id": profile["profile_id"],
        "priority_tier": priority_tier,
        "summary": _summary(priority_tier, findings),
        "rationale": _rationale(priority_tier, findings),
        "findings": [finding.model_dump() for finding in findings],
        "suggested_clinician_review_actions": _suggested_actions(findings, profile),
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload


def _priority_tier(
    findings: list[AbnormalFinding],
    profile_id: str = DEFAULT_PROFILE_ID,
) -> PriorityTier:
    if not findings:
        return "no_unresolved_abnormal_result_found"
    overridden_tiers = [
        override
        for finding in findings
        for override in [priority_override_for_display(finding.display, profile_id)]
        if override
    ]
    if overridden_tiers:
        return highest_priority(overridden_tiers)  # type: ignore[return-value]
    if any(_is_high_potassium(finding) for finding in findings):
        return "same_day_clinician_review_consideration"
    if any(finding.severity == "high" for finding in findings):
        return "soon_clinician_review_consideration"
    if any(finding.severity == "moderate" for finding in findings):
        return "soon_clinician_review_consideration"
    return "routine_clinician_review"


def _is_high_potassium(finding: AbnormalFinding) -> bool:
    return finding.severity == "high" and "potassium" in finding.display.casefold()


def _summary(priority_tier: PriorityTier, findings: list[AbnormalFinding]) -> str:
    if priority_tier == "no_unresolved_abnormal_result_found":
        return "No unresolved abnormal results were found in the synthetic fixture data."
    if priority_tier == "same_day_clinician_review_consideration":
        return _finding_count_summary(
            findings,
            "potentially high-priority unresolved abnormal result",
        )
    if priority_tier == "soon_clinician_review_consideration":
        return _finding_count_summary(
            findings,
            "unresolved abnormal result for timely clinician review",
        )
    return _finding_count_summary(findings, "lower-priority unresolved abnormal result")


def _finding_count_summary(findings: list[AbnormalFinding], phrase: str) -> str:
    count = len(findings)
    plural = "" if count == 1 else "s"
    return f"{count} {phrase}{plural} found for clinician review."


def _rationale(priority_tier: PriorityTier, findings: list[AbnormalFinding]) -> list[str]:
    if not findings:
        return ["No unresolved abnormal result detected by deterministic fixture rules."]

    rationale = [finding.reason for finding in findings]
    severities = sorted({finding.severity for finding in findings})
    rationale.append(f"Finding severity tier(s): {', '.join(severities)}.")
    if priority_tier == "same_day_clinician_review_consideration":
        rationale.append(
            "At least one unresolved high-severity potassium result is present."
        )
    return rationale


def _suggested_actions(
    findings: list[AbnormalFinding],
    profile: dict[str, Any] | None = None,
) -> list[str]:
    if not findings:
        return []
    if profile and profile.get("safety_language"):
        return [str(profile["safety_language"])]
    return [NEUTRAL_REVIEW_ACTION]
