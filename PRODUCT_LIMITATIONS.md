# Product Limitations

## Current Product Status

Aegis Follow-Up is a synthetic-demo-first Prompt Opinion MCP server. It is a
product foundation, not a production clinical system.

## Demo Limitations

- The default workflow uses synthetic FHIR fixture data.
- The public demo does not authenticate users.
- The public demo must not be used with real PHI.
- Task state is demo-oriented and not a persistent clinical workflow database.
- Handoff payloads are not dispatched to external systems.
- Gemini narrative mode is optional and operationally configured.

## FHIR Limitations

- Live FHIR support is limited to context detection and an optional read-only
  Patient reachability proof.
- The optional FHIR proof does not ingest Observations, DiagnosticReports,
  ServiceRequests, Tasks, or Conditions into clinical logic.
- The main abnormal-result workflow does not depend on live FHIR.
- Read-only production ingestion is future roadmap work.

## Workflow Limitations

- No persistent team queue exists yet.
- No clinician identity or role model exists yet.
- No dismissal-reason persistence exists yet.
- No customer tenant model exists yet.
- No operational analytics or service-level reporting exists yet.

## EHR Writeback Limitations

Aegis Follow-Up does not write to an EHR today. It does not create Tasks, draft
notes, CommunicationRequests, orders, appointments, or patient messages in a live
system.

Any future writeback must be optional, scoped, audited, customer-reviewed, and
clinician-approved before execution.

## Clinical Limitations

- Rule profiles require clinician review before use in real settings.
- Synthetic fixtures are not clinical validation data.
- The system may produce false positives or false negatives.
- The AI narrative can be unavailable; deterministic fallback is expected.
- The product is not emergency triage or treatment advice.

## Production Limitations

Production readiness requires additional work: authentication, tenant isolation,
PHI-safe observability, audit storage, security review, privacy review, support
model, incident response, BAA/privacy posture where applicable, and clinical
validation planning.
