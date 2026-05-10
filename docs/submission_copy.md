# Devpost Submission Copy

## Project Name

Follow-Up Radar MCP

## Tagline

Rules decide. AI synthesizes. Safety validates. Clinician remains in control.

## Short Description

Follow-Up Radar is a Prompt Opinion-ready MCP server that reviews synthetic FHIR
data for potentially unresolved abnormal results, explains deterministic audit
decisions, prioritizes a follow-up queue, and optionally generates a guarded
clinician-review narrative from the structured evidence.

## What It Does

The server exposes MCP tools for synthetic patient snapshots, observations,
abnormal-result detection, deterministic follow-up briefs, rule-profile priority
assessment, audit trail explanations, task queue workflow state, EHR integration
positioning, FHIR connection transparency, payload-only agent handoff, and
controlled AI narrative synthesis.

## AI Factor

The AI layer is intentionally constrained. Deterministic services decide the facts:
which results are abnormal, which are suppressed by follow-up evidence, which
priority tier applies, and which tasks are open. The optional Gemini path only
synthesizes a short narrative from that structured output. Safety validation blocks
unsafe recommendation wording and falls back to deterministic text when needed.
The final demo shows the AI output beside the structured findings, priority, and
audit summary so judges can see that the model is not the source of truth.

## Impact

The project demonstrates how an MCP server could help a care team spot follow-up
gaps without replacing clinician judgment. The workflow is designed around audit
evidence, task review, and clinician confirmation before any production EHR action.
The handoff payload shows how the same result could later move into scheduling,
care coordination, or EHR-task workflows after human review.

## Feasibility

The demo is deployable today as a Docker-backed Render service with health checks,
smoke tests, Prompt Opinion FHIR-context capability advertising, fixture-mode
fallback, and no required secrets. The path to production would add real FHIR reads,
persistent audit storage, HIPAA-eligible hosting, access controls, and reviewed EHR
write workflows.
`get_fhir_connection_status` makes the current demo boundary explicit by reporting
fixture mode and active data source instead of implying live FHIR reads.

## Safety

This build uses synthetic data only. It does not contain PHI, does not request
`offline_access`, does not handle refresh tokens, does not perform real FHIR or EHR
writes, and does not diagnose, prescribe, or issue treatment directives.
The handoff payload is schema/demo output only and does not contact another agent.

## Demo Flow

1. Show Prompt Opinion or MCP Inspector connected to the deployed `/mcp/` endpoint.
2. List follow-up tasks and show the priority queue.
3. Explain deterministic decisions for `synthetic-patient-001`.
4. Show FHIR connection status and active fixture data source.
5. Generate the AI follow-up brief and show narrative plus structured evidence.
6. Show safety validation and fallback fields.
7. Create the payload-only handoff for `synthetic-patient-003`.
8. Show the EHR integration summary with dynamic workflow metrics.
