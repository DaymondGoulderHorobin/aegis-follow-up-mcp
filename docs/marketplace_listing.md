# Marketplace Listing

## Product Name

Aegis Follow-Up

Logo asset: `docs/assets/aegis-follow-up-logo.svg`

## Tagline

Aegis Follow-Up is a clinician-review MCP safety layer that turns patient-context
data into auditable follow-up tasks, controlled AI summaries, and handoff-ready
payloads.

## Short Description

Aegis Follow-Up helps clinicians surface potentially unresolved abnormal results,
understand why each result was flagged or suppressed, prioritize follow-up tasks,
and generate guarded AI summaries for clinician review. The system combines
deterministic clinical logic with a controlled generative layer, using audit trails
and safety validation so AI assists with synthesis but never replaces clinical
judgement.

## Endpoint

```text
https://follow-up-radar-mcp.onrender.com/mcp/
```

## Transport

Streamable HTTP.

## Authentication

None for the hackathon synthetic-data demo.

## Prompt Opinion FHIR Context

Supported. The server advertises optional FHIR-context scopes during MCP
initialize. Users can leave the trust toggle disabled and still use the synthetic
fixture workflow.

## Production Note

The demo uses synthetic fixture data by default. It does not require PHI, does not
perform real EHR writes, and does not perform live FHIR reads unless a future
production mode is explicitly implemented and validated.

## Recommended Demo Prompts

```text
Show the FHIR connection status for Aegis Follow-Up and explain whether live FHIR reads occurred.
```

```text
List the follow-up task queue using the default primary care profile.
```

```text
Explain why synthetic-patient-003 is high priority and show the deterministic audit trail.
```

```text
Generate an AI follow-up brief for synthetic-patient-003 and show the deterministic evidence fields.
```

```text
Create a follow-up handoff payload for synthetic-patient-003 without sending it anywhere.
```

## Safety Statement

Clinical decision support only. For clinician review. Not a diagnosis or treatment
directive. The demo uses synthetic fixture data only, requests no `offline_access`,
handles no refresh tokens, performs no real EHR writes, and does not autonomously
dispatch handoff payloads.

## AI Factor

Prompt Opinion is the client-side AI layer that chooses MCP tools. Aegis Follow-Up
is the MCP-side safety layer that performs deterministic review and can optionally
use Gemini for concise narrative synthesis from structured source evidence. Gemini
does not decide clinical facts. Deterministic findings, priority tier, audit trail,
and task context remain the source of truth.

## Potential Impact

Aegis Follow-Up targets the operational gap between abnormal results and documented
follow-up. It gives clinicians a queue, audit rationale, review status, and
handoff-ready payloads that can later support scheduling or care-coordination
workflows after human review.

## Feasibility

The system is deployed as a Docker-backed Render service with health checks, smoke
tests, deterministic fallback mode, Prompt Opinion FHIR-context compatibility, and
optional Gemini narrative mode controlled by environment variables.
