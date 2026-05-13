# Pilot Runbook

This runbook outlines how to operate a controlled Aegis Follow-Up pilot after
customer approval. It is not a production operations manual.

## Pilot Preconditions

- Customer approval for scope and data access.
- Authentication and tenant-aware deployment plan.
- Privacy and security review.
- Clinical safety review.
- Read-only FHIR posture unless writeback is separately approved.
- PHI-safe logging and support process.

## Setup

1. Confirm the environment profile: `staging` or `pilot`.
2. Confirm synthetic fixture smoke tests pass.
3. Configure managed secrets in the deployment platform only.
4. Confirm `LIVE_FHIR_READS_ENABLED=false` until explicit read-only validation.
5. Confirm `LLM_PROVIDER=disabled` unless Gemini validation is approved.
6. Run fallback MCP smoke.
7. Validate Prompt Opinion tool discovery.
8. Review safety disclaimers and prohibited claims with pilot users.

## Demo Flow

Use the five-tool path first:

1. `get_fhir_connection_status`
2. `list_follow_up_tasks`
3. `explain_result_decisions` for `synthetic-patient-003`
4. `generate_ai_follow_up_brief` for `synthetic-patient-003`
5. `create_follow_up_handoff_payload` for `synthetic-patient-003`

Only after the primary flow succeeds, show optional Gemini mode or optional FHIR
reachability if the pilot environment is approved for those tests.

## Operational Checks

- `/healthz`
- `/readyz`
- `/version`
- MCP smoke script
- Prompt Opinion tool discovery
- FHIR-context extension display
- Safety wording in generated outputs
- No token or PHI exposure in logs

## Incident Handling

If a safety, privacy, or integration incident occurs:

1. Stop the demo or pilot workflow.
2. Disable optional live FHIR proof or Gemini mode if relevant.
3. Preserve non-PHI operational logs.
4. Do not copy PHI into issues, chat, or support tickets.
5. Notify the pilot owner and security/privacy contact.
6. Document root cause and mitigation before re-enabling.

## Rollback

- Restore `LIVE_FHIR_READS_ENABLED=false`.
- Restore `LLM_PROVIDER=disabled`.
- Revert to synthetic fixture validation.
- Redeploy the last known good container image or commit.
- Confirm fallback MCP smoke passes.

## Support Model

Pilot support should define:

- technical owner;
- clinical workflow owner;
- security/privacy contact;
- support hours;
- escalation path;
- issue intake rules that prohibit PHI and secrets.

## Success Metrics

Potential pilot metrics:

- unresolved abnormal-result queue volume;
- percentage of items reviewed;
- median time to review;
- dismissal reasons;
- false positive themes;
- missed follow-up evidence themes;
- clinician usability feedback;
- safety validation fallback rate.

## Exit Criteria

- Pilot users understand the product boundaries.
- No PHI or tokens are exposed in logs or issues.
- Findings are reviewed by clinicians.
- Audit output is understandable.
- Workflow burden is acceptable.
- Next-phase requirements are documented.
