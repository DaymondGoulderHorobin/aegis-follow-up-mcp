# Production Readiness Checklist

This checklist defines what must exist before Aegis Follow-Up is considered ready
for real clinical production use. The current repository does not claim production
readiness.

## Product And Safety

- [ ] Clinical safety statement reviewed by qualified advisors.
- [ ] Prohibited claims reviewed in all user-facing copy.
- [ ] False positive and false negative handling documented.
- [ ] Human review workflow defined.
- [ ] Emergency and urgent-care disclaimers reviewed.
- [ ] Customer-specific clinical thresholds approved.

## Authentication And Tenanting

- [ ] Authentication required for PHI-bearing deployments.
- [ ] Tenant isolation model implemented and tested.
- [ ] Role model defined for clinicians, administrators, and support users.
- [ ] Access review process documented.
- [ ] Session and token handling reviewed.

## FHIR And Data Access

- [ ] Read-only FHIR ingestion implemented before any writeback.
- [ ] Required FHIR resources and scopes documented.
- [ ] No `offline_access` unless separately justified and approved.
- [ ] Refresh-token handling reviewed before implementation.
- [ ] Data quality diagnostics available.
- [ ] Sandbox and pilot FHIR behavior covered by tests.

## Privacy And Security

- [ ] PHI-safe logging verified.
- [ ] Raw FHIR payload logging disabled.
- [ ] Secrets managed through deployment secret storage.
- [ ] Dependency and vulnerability review completed.
- [ ] Incident response process documented.
- [ ] Privacy posture and BAA requirements reviewed where applicable.

## Observability And Operations

- [ ] Structured logs avoid PHI and tokens.
- [ ] Metrics cover queue volume, review latency, errors, and fallback rates.
- [ ] Alerts defined for service health and integration failures.
- [ ] Runbook covers rollback, support, and incident escalation.
- [ ] Backup and retention assumptions documented.

## AI Governance

- [ ] AI prompts are constrained to structured evidence.
- [ ] Deterministic findings remain the source of truth.
- [ ] Safety validation is monitored.
- [ ] Fallback behavior is tested.
- [ ] LLM provider data-processing terms are reviewed.

## EHR Writeback

- [ ] Writeback remains disabled by default.
- [ ] Every write requires clinician approval.
- [ ] Minimal write scopes are documented.
- [ ] Dry-run mode exists.
- [ ] Full audit logs exist for proposed, approved, attempted, and completed writes.
- [ ] Customer-specific legal/security review is complete.

## Support And Commercial Readiness

- [ ] Support owner and response expectations defined.
- [ ] Customer onboarding checklist exists.
- [ ] Pilot success metrics defined.
- [ ] Product analytics avoid PHI.
- [ ] Pricing and contract assumptions reviewed.
- [ ] Clinical validation study plan drafted where required.
