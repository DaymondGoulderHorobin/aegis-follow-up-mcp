"""Deterministic abnormal result detection for synthetic observations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.fhir.fixtures import default_patient_id, iter_resources, load_synthetic_bundle
from app.fhir.models import AbnormalFinding
from app.services.observations import get_recent_observations

ABNORMAL_INTERPRETATIONS = {"H", "HH", "L", "LL", "A", "AA"}
FOLLOW_UP_RESOURCE_TYPES = {
    "Appointment",
    "CarePlan",
    "DiagnosticReport",
    "MedicationRequest",
    "Procedure",
    "ServiceRequest",
}


def find_unresolved_abnormal_results(
    patient_id: str | None = None,
    bundle: dict[str, Any] | None = None,
) -> list[AbnormalFinding]:
    source_bundle = bundle or load_synthetic_bundle()
    requested_patient_id = patient_id or default_patient_id(source_bundle)
    findings: list[AbnormalFinding] = []
    observations = get_recent_observations(
        patient_id=requested_patient_id,
        bundle=source_bundle,
    )
    for observation in observations:
        if not observation.abnormal:
            continue
        if _has_follow_up_evidence(observation.id, observation.effective_date, source_bundle):
            continue

        findings.append(
            AbnormalFinding(
                observation_id=observation.id,
                display=observation.display,
                severity=_severity_for_observation(
                    observation.value,
                    observation.reference_low,
                    observation.reference_high,
                    observation.interpretation,
                ),
                reason=(
                    f"{observation.display} is marked abnormal and no follow-up evidence "
                    "is present in the synthetic fixture bundle."
                ),
                evidence=[
                    f"{observation.display}: {observation.value:g} {observation.unit}",
                    f"Effective date: {observation.effective_date}",
                    _reference_text(observation.reference_low, observation.reference_high),
                ],
                suggested_clinician_review_action=(
                    "Clinician may wish to review the result, confirm follow-up status, "
                    "and document the plan if appropriate."
                ),
            )
        )
    return findings


def _has_follow_up_evidence(
    observation_id: str,
    observation_date: str,
    bundle: dict[str, Any],
) -> bool:
    observed_at = _parse_date(observation_date)
    if observed_at is None:
        return False
    for resource in iter_resources(bundle=bundle):
        if resource.get("resourceType") not in FOLLOW_UP_RESOURCE_TYPES:
            continue
        if not _references_observation(resource, observation_id):
            continue
        follow_up_date = _resource_date(resource)
        if follow_up_date is None or follow_up_date >= observed_at:
            return True
    return False


def _references_observation(resource: dict[str, Any], observation_id: str) -> bool:
    expected_reference = f"Observation/{observation_id}"
    return expected_reference in _extract_references(resource)


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


def _date_from_period(resource: dict[str, Any]) -> str | None:
    period = resource.get("period")
    if isinstance(period, dict):
        start = period.get("start")
        if isinstance(start, str):
            return start
    return None


def _first_string(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and value:
            return value
    return None


def _date_from_nested(resource: dict[str, Any]) -> str | None:
    occurrence = resource.get("occurrencePeriod")
    if isinstance(occurrence, dict):
        start = occurrence.get("start")
        if isinstance(start, str):
            return start
    timing = resource.get("occurrenceTiming")
    if isinstance(timing, dict):
        event = timing.get("event")
        if isinstance(event, list):
            for item in event:
                if isinstance(item, str):
                    return item
    return None


def _safe_parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _resource_date(resource: dict[str, Any]) -> datetime | None:
    value = _first_string(
        resource.get("authoredOn"),
        resource.get("occurrenceDateTime"),
        _date_from_nested(resource),
        resource.get("effectiveDateTime"),
        resource.get("issued"),
        resource.get("created"),
        resource.get("performedDateTime"),
        _date_from_period(resource),
    )
    return _safe_parse_date(value)


def _parse_date(value: str) -> datetime | None:
    return _safe_parse_date(value)


def _severity_for_observation(
    value: float,
    reference_low: float | None,
    reference_high: float | None,
    interpretation: str | None,
) -> str:
    if interpretation in {"HH", "LL", "AA"}:
        return "high"
    if reference_high is not None and value > reference_high:
        ratio = value / reference_high
        if ratio >= 1.5:
            return "high"
        if ratio >= 1.2:
            return "moderate"
    if reference_low is not None and reference_low > 0 and value < reference_low:
        ratio = value / reference_low
        if ratio <= 0.5:
            return "high"
        if ratio <= 0.8:
            return "moderate"
    return "low"


def _reference_text(reference_low: float | None, reference_high: float | None) -> str:
    if reference_low is None and reference_high is None:
        return "Reference range: not provided"
    if reference_low is None:
        return f"Reference range: <= {reference_high:g}"
    if reference_high is None:
        return f"Reference range: >= {reference_low:g}"
    return f"Reference range: {reference_low:g}-{reference_high:g}"
