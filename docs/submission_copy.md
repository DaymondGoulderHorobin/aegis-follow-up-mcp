# Submission Copy

## Project Name

Aegis Follow-Up

## Tagline

Rules decide. AI synthesizes. Safety validates. Clinician remains in control.

## Short Description

Aegis Follow-Up helps clinicians surface potentially unresolved abnormal results,
understand why each result was flagged or suppressed, prioritize follow-up tasks,
and generate guarded AI summaries for clinician review.

## What It Does

Aegis Follow-Up is a Prompt Opinion-ready MCP server. It exposes tools for
synthetic patient snapshots, observation review, abnormal-result detection,
deterministic follow-up briefs, rule-profile priority assessment, audit trail
explanations, task queue workflow state, FHIR connection transparency, optional
read-only FHIR reachability proof, payload-only agent handoff, EHR integration
positioning, and controlled AI narrative synthesis.

## AI Factor

The project uses two AI layers with a clear safety boundary. Prompt Opinion uses AI
to interpret the user request and choose MCP tools. Aegis Follow-Up performs
deterministic clinical review, then optionally calls Gemini to synthesize a concise
narrative from structured deterministic evidence. Gemini cannot change findings,
priority tiers, audit decisions, or task state. Safety validation blocks unsafe
wording and falls back to deterministic text if needed.

## Potential Impact

Abnormal result follow-up is a real care-operations problem. Aegis Follow-Up shows
how an MCP server can turn patient-context data into an auditable follow-up queue,
explain why each result needs review, and prepare payloads that future scheduling or
care-coordination agents could consume after human review.

## Feasibility

The demo is deployable today as a Docker-backed Render service with health checks,
smoke tests, Prompt Opinion FHIR-context capability advertising, fixture-mode
fallback, optional Gemini narrative mode, optional FHIR connectivity proof, and no
required secrets for the default demo. The path to production is clear:
HIPAA-eligible hosting, BAA coverage, persistent audit storage, tenant-aware access
controls, monitoring, security review, and explicitly reviewed EHR write workflows.

## Safety

The hackathon demo uses synthetic fixture data only. It does not contain PHI, does
not request `offline_access`, does not handle refresh tokens, does not perform real
FHIR reads by default, does not write to an EHR, does not contact another agent, and
does not diagnose, prescribe, or issue treatment directives. The optional
connectivity proof returns safe metadata only and never returns tokens or full FHIR
payloads.

## Demo Flow

1. Show `get_fhir_connection_status` and confirm synthetic fixture mode.
2. Show `list_follow_up_tasks` and the high-priority potassium case.
3. Show `explain_result_decisions` and the deterministic audit trail.
4. Show `generate_ai_follow_up_brief` with structured evidence beside the narrative.
5. Show `create_follow_up_handoff_payload` with payload-only safety flags.
