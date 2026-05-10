"""EHR integration story for the workflow-layer demo."""

from __future__ import annotations

from typing import Any

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)


def get_ehr_integration_summary() -> dict[str, Any]:
    """Return the current and future EHR integration story."""

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
        "demo_state_only": True,
        "ehr_write_performed": False,
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload
