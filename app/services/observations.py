"""Observation extraction and normalization."""

from __future__ import annotations

from typing import Any

from app.fhir.fixtures import iter_resources, load_synthetic_bundle
from app.fhir.models import ObservationResult

ABNORMAL_INTERPRETATIONS = {"H", "HH", "L", "LL", "A", "AA"}


def get_recent_observations(
    patient_id: str | None = None,
    bundle: dict[str, Any] | None = None,
) -> list[ObservationResult]:
    source_bundle = bundle or load_synthetic_bundle()
    observations = [
        _normalize_observation(resource)
        for resource in iter_resources("Observation", source_bundle)
        if _matches_patient(resource, patient_id)
    ]
    return sorted(observations, key=lambda item: item.effective_date, reverse=True)


def _matches_patient(resource: dict[str, Any], patient_id: str | None) -> bool:
    if patient_id is None:
        return True
    return resource.get("subject", {}).get("reference") == f"Patient/{patient_id}"


def _normalize_observation(resource: dict[str, Any]) -> ObservationResult:
    value_quantity = resource.get("valueQuantity", {})
    reference_range = (resource.get("referenceRange") or [{}])[0]
    low = reference_range.get("low", {}).get("value")
    high = reference_range.get("high", {}).get("value")
    interpretation = _interpretation_code(resource)
    value = float(value_quantity.get("value"))
    reference_low = float(low) if low is not None else None
    reference_high = float(high) if high is not None else None

    return ObservationResult(
        id=resource["id"],
        code=_code(resource),
        display=_display(resource),
        effective_date=resource.get("effectiveDateTime", ""),
        value=value,
        unit=value_quantity.get("unit", ""),
        interpretation=interpretation,
        reference_low=reference_low,
        reference_high=reference_high,
        abnormal=_is_abnormal(value, reference_low, reference_high, interpretation),
    )


def _code(resource: dict[str, Any]) -> str:
    coding = (resource.get("code", {}).get("coding") or [{}])[0]
    return coding.get("code", "")


def _display(resource: dict[str, Any]) -> str:
    code = resource.get("code", {})
    if code.get("text"):
        return code["text"]
    coding = (code.get("coding") or [{}])[0]
    return coding.get("display", coding.get("code", "Observation"))


def _interpretation_code(resource: dict[str, Any]) -> str | None:
    interpretation = resource.get("interpretation") or []
    if not interpretation:
        return None
    coding = interpretation[0].get("coding") or []
    if not coding:
        return None
    return coding[0].get("code")


def _is_abnormal(
    value: float,
    reference_low: float | None,
    reference_high: float | None,
    interpretation: str | None,
) -> bool:
    if interpretation in ABNORMAL_INTERPRETATIONS:
        return True
    if reference_low is not None and value < reference_low:
        return True
    if reference_high is not None and value > reference_high:
        return True
    return False
