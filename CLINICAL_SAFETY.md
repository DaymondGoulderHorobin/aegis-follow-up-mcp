# Clinical Safety

## Safety Statement

Aegis Follow-Up is clinical decision support only. It is for clinician review. It
is not a diagnosis or treatment directive.

The product is designed to help clinicians find and review potentially unresolved
abnormal results. It does not replace clinical judgement and does not perform
autonomous clinical actions.

## Allowed Claims

It is appropriate to say that Aegis Follow-Up:

- surfaces potentially unresolved abnormal results from synthetic fixture data;
- groups follow-up tasks by deterministic priority tiers;
- explains why a result was flagged or suppressed;
- generates guarded summaries from deterministic evidence;
- creates payload-only handoff data for future workflows;
- can optionally prove read-only FHIR Patient reachability when configured.

## Prohibited Claims

Do not claim that Aegis Follow-Up:

- diagnoses a patient;
- prescribes medication;
- recommends treatment or therapy;
- provides emergency triage advice;
- autonomously contacts patients, schedules visits, or dispatches handoffs;
- writes to an EHR;
- has been clinically validated for production use;
- guarantees that all unresolved abnormal results will be found.

## Deterministic Source Of Truth

Deterministic logic remains the source of truth for findings, priority tiers,
audit decisions, and handoff context. AI output is optional narrative synthesis
from structured evidence and must not introduce new clinical facts or actions.

## Human Review Requirement

A clinician must review all findings, task priorities, AI narratives, dismissal
reasons, handoff payloads, and any future EHR writeback before action is taken.

Human approval is required before any future write, communication request, task
creation, note creation, or care-coordination handoff.

## False Positive And False Negative Risk

The system may flag items that have already been handled, and it may miss items if
available data is incomplete or follow-up evidence is not represented. Audit
output, dismissal reasons, and clinician review are required controls.

## Advisor Review Before Pilot

Before real clinical pilot use, clinical safety language, thresholds, rule
profiles, workflow assumptions, and escalation language should be reviewed with
qualified clinical advisors and customer governance stakeholders.
