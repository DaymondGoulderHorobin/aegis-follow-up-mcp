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
positioning, and controlled AI narrative synthesis.

## AI Factor

The AI layer is intentionally constrained. Deterministic services decide the facts:
which results are abnormal, which are suppressed by follow-up evidence, which
priority tier applies, and which tasks are open. The optional Gemini path only
synthesizes a short narrative from that structured output. Safety validation blocks
unsafe recommendation wording and falls back to deterministic text when needed.

## Impact

The project demonstrates how an MCP server could help a care team spot follow-up
gaps without replacing clinician judgment. The workflow is designed around audit
evidence, task review, and clinician confirmation before any production EHR action.

## Feasibility

The demo is deployable today as a Docker-backed Render service with health checks,
smoke tests, Prompt Opinion FHIR-context capability advertising, fixture-mode
fallback, and no required secrets. The path to production would add real FHIR reads,
persistent audit storage, HIPAA-eligible hosting, access controls, and reviewed EHR
write workflows.

## Safety

This build uses synthetic data only. It does not contain PHI, does not request
`offline_access`, does not handle refresh tokens, does not perform real FHIR or EHR
writes, and does not diagnose, prescribe, or issue treatment directives.

## Demo Flow

1. Show Prompt Opinion or MCP Inspector connected to the deployed `/mcp/` endpoint.
2. List follow-up tasks and show the priority queue.
3. Explain deterministic decisions for `synthetic-patient-001`.
4. Generate the AI follow-up brief and show narrative plus structured evidence.
5. Show safety validation and fallback fields.
6. Show the EHR integration summary with dynamic workflow metrics.
