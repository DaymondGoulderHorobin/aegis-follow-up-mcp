# Post-Hackathon Commercial Roadmap

This roadmap describes how Aegis Follow-Up could evolve from a hackathon-ready
Prompt Opinion MCP demo into a commercial clinical operations product.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Phase 1: Pilot Hardening

Goal: make the existing synthetic and optional-AI demo reliable enough for
structured pilot conversations.

- Keep the synthetic demo path as the stable test harness.
- Add production configuration profiles for local, staging, demo, and pilot modes.
- Improve structured logging without logging tokens or PHI.
- Add role-aware audit events for clinician, administrator, and integration actions.
- Expand synthetic fixtures across more result types, specialties, and follow-up
  evidence patterns.
- Add explicit demo/pilot environment banners in operational docs.
- Review clinical safety language with practicing clinicians and compliance advisors.
- Create a pilot runbook covering setup, demo flow, support, rollback, and incident
  response.

Exit criteria:

- Reproducible staging deployment.
- Expanded fixtures and tests.
- Advisor-reviewed safety language.
- Clear pilot operating checklist.

## Phase 2: Real FHIR Read Integration

Goal: replace the narrow connectivity proof with real read-only ingestion while
keeping synthetic tests and deterministic safety controls.

- Keep read-only mode as the first production posture.
- Support read ingestion for:
  - Patient
  - Observation
  - DiagnosticReport
  - ServiceRequest
  - Task
  - Encounter
  - Condition
  - MedicationStatement
- Map follow-up evidence more robustly across notes, tasks, orders, encounters, and
  recent result trends.
- Add tenant/profile-specific thresholds and rule configuration.
- Preserve deterministic audit trails for every flagged and suppressed result.
- Add data quality diagnostics for missing, stale, duplicated, or conflicting FHIR
  resources.
- Keep synthetic fixture regression tests for every live-FHIR mapping rule.

Exit criteria:

- Read-only FHIR ingestion works in a controlled pilot tenant.
- Deterministic decisions remain explainable.
- No live FHIR data is used without customer authorization and security review.

## Phase 3: Human-In-The-Loop Workflow

Goal: turn the demo queue into a reviewed clinical operations workflow.

- Add persistent task state.
- Add clinician review workflow.
- Support dismissal reasons and follow-up documentation state.
- Add team queues by role, panel, location, and specialty.
- Provide exportable audit trails.
- Add review timestamps and reviewer identity.
- Track handoff payload generation without dispatching autonomous clinical actions.
- Add operational metrics for queue volume, review timeliness, and unresolved items.

Exit criteria:

- Clinicians can review, dismiss, document, and export follow-up decisions.
- Every state transition is audited.
- No autonomous clinical action is performed.

## Phase 4: EHR Writeback, Carefully Scoped

Goal: introduce optional EHR writes only after customer-specific review and explicit
clinician approval.

- Optional Task creation.
- Optional draft note creation.
- Optional CommunicationRequest or care-coordination handoff.
- Require clinician approval before any write.
- Maintain a full audit log of proposed, approved, attempted, and completed writes.
- Add customer-specific legal, privacy, security, and clinical safety review.
- Add dry-run mode and rollback/support playbooks.
- Limit write scopes to the minimum needed for each customer workflow.

Exit criteria:

- Writeback is disabled by default.
- Every write is human-approved.
- Customer-specific governance and safety review is complete.

## Phase 5: Commercialization

Goal: package Aegis Follow-Up for repeatable Prompt Opinion marketplace and clinic
pilot adoption.

- Finalize Prompt Opinion marketplace listing.
- Create a clinic pilot package with scope, setup, training, and support materials.
- Complete security review and dependency/process hardening.
- Define BAA and privacy posture where applicable.
- Develop pricing hypothesis for clinic pilots and commercial subscriptions.
- Define support model, incident response expectations, and update cadence.
- Add product analytics that avoid PHI and support value measurement.
- Design a clinical validation study with advisor input.
- Document target buyer, user, workflow owner, and success metrics.

Exit criteria:

- Marketplace listing and pilot package are ready.
- Security/privacy posture is documented.
- Commercial assumptions are testable with pilot customers.

## Cross-Phase Product Principles

- Keep deterministic logic and auditability as the source of truth.
- Keep AI narrative synthesis constrained to structured evidence.
- Keep clinician review required for clinical decisions and writeback.
- Avoid autonomous clinical actions.
- Treat live FHIR data as sensitive and customer-governed.
- Preserve synthetic fixture tests as the regression backbone.

## Related Risk Register

See `docs/risk_register.md` for risks and mitigations that should remain active
through all roadmap phases.
