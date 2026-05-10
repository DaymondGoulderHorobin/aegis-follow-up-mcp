"""Clinician note drafting for review."""

from __future__ import annotations

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import assert_clinician_facing_text_safe
from app.services.abnormal_results import find_unresolved_abnormal_results
from app.services.patient_snapshot import get_patient_snapshot


def draft_clinician_note(patient_id: str | None = None) -> str:
    patient = get_patient_snapshot(patient_id=patient_id)
    findings = find_unresolved_abnormal_results(patient_id=patient_id)
    if not findings:
        note = (
            f"{CLINICIAN_REVIEW_DISCLAIMER} Synthetic chart review for {patient.name} "
            "did not identify unresolved abnormal results in the fixture data."
        )
        assert_clinician_facing_text_safe(note)
        return note

    finding_lines = "; ".join(
        f"{finding.display} ({finding.severity})" for finding in findings
    )
    note = (
        f"{CLINICIAN_REVIEW_DISCLAIMER} Synthetic chart review for {patient.name} identified "
        f"potentially unresolved abnormal result(s): {finding_lines}. "
        "Clinician may wish to verify whether follow-up is already documented and "
        "update the chart with review notes if appropriate."
    )
    assert_clinician_facing_text_safe(note)
    return note
