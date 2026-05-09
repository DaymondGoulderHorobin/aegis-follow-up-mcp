"""Pydantic models returned by services and MCP tools."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ObservationResult(BaseModel):
    id: str
    code: str
    display: str
    effective_date: str
    value: float
    unit: str
    interpretation: str | None = None
    reference_low: float | None = None
    reference_high: float | None = None
    abnormal: bool = False


class AbnormalFinding(BaseModel):
    observation_id: str
    display: str
    severity: str
    reason: str
    evidence: list[str] = Field(default_factory=list)
    suggested_clinician_review_action: str


class PatientSnapshot(BaseModel):
    patient_id: str
    name: str
    birth_date: str
    sex: str
    conditions: list[str]
    medications: list[str]
    recent_encounters: list[str]
