"""Patient snapshot construction from synthetic FHIR fixtures."""

from __future__ import annotations

from typing import Any

from app.fhir.fixtures import first_resource, iter_resources, load_synthetic_bundle
from app.fhir.models import PatientSnapshot


def get_patient_snapshot(
    patient_id: str | None = None,
    bundle: dict[str, Any] | None = None,
) -> PatientSnapshot:
    source_bundle = bundle or load_synthetic_bundle()
    patient = first_resource("Patient", source_bundle)
    requested_id = patient_id or patient.get("id", "synthetic-patient")

    return PatientSnapshot(
        patient_id=requested_id,
        name=_patient_name(patient),
        birth_date=patient.get("birthDate", ""),
        sex=patient.get("gender", ""),
        conditions=[
            _code_text(resource)
            for resource in iter_resources("Condition", source_bundle)
            if _matches_patient(resource, requested_id)
        ],
        medications=[
            _medication_text(resource)
            for resource in iter_resources("MedicationStatement", source_bundle)
            if _matches_patient(resource, requested_id)
        ],
        recent_encounters=[
            _encounter_text(resource)
            for resource in iter_resources("Encounter", source_bundle)
            if _matches_patient(resource, requested_id)
        ],
    )


def _matches_patient(resource: dict[str, Any], patient_id: str) -> bool:
    subject = resource.get("subject") or resource.get("patient") or {}
    return subject.get("reference") == f"Patient/{patient_id}"


def _patient_name(patient: dict[str, Any]) -> str:
    name = (patient.get("name") or [{}])[0]
    given = " ".join(name.get("given", []))
    family = name.get("family", "")
    return " ".join(part for part in (given, family) if part) or "Synthetic Patient"


def _code_text(resource: dict[str, Any]) -> str:
    code = resource.get("code", {})
    if code.get("text"):
        return code["text"]
    coding = (code.get("coding") or [{}])[0]
    return coding.get("display", coding.get("code", "Unknown"))


def _medication_text(resource: dict[str, Any]) -> str:
    medication = resource.get("medicationCodeableConcept", {})
    if medication.get("text"):
        return medication["text"]
    coding = (medication.get("coding") or [{}])[0]
    return coding.get("display", coding.get("code", "Unknown medication"))


def _encounter_text(resource: dict[str, Any]) -> str:
    encounter_type = _code_text(resource) if resource.get("code") else "Encounter"
    start = resource.get("period", {}).get("start", "unknown date")
    return f"{encounter_type} on {start}"
