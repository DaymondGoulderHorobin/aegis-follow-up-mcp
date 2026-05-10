"""Template-based follow-up brief generation."""

from __future__ import annotations

from typing import Any

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)
from app.services.abnormal_results import find_unresolved_abnormal_results
from app.services.patient_snapshot import get_patient_snapshot


def generate_follow_up_brief(patient_id: str | None = None) -> dict[str, Any]:
    patient = get_patient_snapshot(patient_id=patient_id)
    findings = find_unresolved_abnormal_results(patient_id=patient_id)
    finding_payload = [finding.model_dump() for finding in findings]

    if findings:
        summary = (
            f"{len(findings)} potentially unresolved abnormal result"
            f"{'' if len(findings) == 1 else 's'} found for clinician review."
        )
    else:
        summary = "No unresolved abnormal results were found in the synthetic fixture data."

    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "patient": {
            "patient_id": patient.patient_id,
            "name": patient.name,
            "birth_date": patient.birth_date,
            "sex": patient.sex,
        },
        "summary": summary,
        "findings": finding_payload,
        "clinician_review_actions": [
            finding.suggested_clinician_review_action for finding in findings
        ],
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload
