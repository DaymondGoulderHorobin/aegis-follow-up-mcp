# Commercial Workflow

Follow-Up Radar is positioned as a deterministic follow-up safety layer that can sit between FHIR data and clinician-reviewed workflow action.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Product Workflow

1. Prompt Opinion or another MCP client connects to the deployed MCP endpoint.
2. The server receives optional FHIR context headers, or uses synthetic fixtures in demo mode.
3. Deterministic rules inspect recent observations and documented follow-up evidence.
4. Audit trail entries explain why each relevant result was flagged or suppressed.
5. The task queue groups unresolved findings by clinician-review priority.
6. Optional AI synthesis produces a concise narrative from the deterministic evidence.
7. FHIR connection status explains whether the active data source is fixture data or a future live FHIR path.
8. A payload-only handoff schema shows how another workflow agent could consume the task after human review.
9. Demo workflow state can mark tasks as reviewed, follow-up documented, or dismissed with a reason.
10. Production integration could create clinician-reviewed EHR tasks or notes after human confirmation.

## Buyer Value

- Auditability: each result has a rule ID, evidence, and decision reason.
- Configurability: static profiles show how clinics can tune deterministic workflow emphasis.
- Operational workflow: task queues make unresolved follow-up work visible by priority.
- Controlled AI: narrative generation is optional, guarded, and backed by deterministic fallback.
- FHIR transparency: the status tool reports header presence and active fixture mode.
- Integration readiness: the handoff payload is structured for future scheduling, care coordination, or EHR-task agents.
- Human-in-the-loop safety: the demo workflow records review state and states that no EHR write occurred.
- Integration credibility: the EHR summary describes FHIR-in and clinician-reviewed task or note out.

## Current Demo Boundaries

- Synthetic fixture data only.
- No real PHI.
- No real external FHIR reads.
- No EHR writes.
- No autonomous handoff dispatch.
- No refresh tokens.
- No `offline_access`.
- Optional LLM summarisation only; deterministic rules remain the source of truth.
- No autonomous clinical actions.

## EHR Integration Story

Current demo mode is FHIR context and synthetic fixture read path only.

Future production path:

```text
FHIR context in -> deterministic follow-up review -> clinician-reviewed task or note out
```

Possible future EHR write targets include `Task`, `CommunicationRequest`, `DocumentReference`, or a clinician-reviewed note draft. Any such write would require explicit clinician confirmation and production-grade authentication, authorization, audit logging, and governance.

## A2A-Style Handoff

`create_follow_up_handoff_payload` demonstrates the shape of a future agent handoff
without performing transport. It returns patient ID, task ID, finding display,
priority tier, audit decision ID, and safety flags such as `required_human_review`,
`payload_only`, and `ehr_write_performed: false`.
