# Judge Testing Guide

## What To Test

Use the deployed MCP endpoint:

```text
https://aegis-follow-up-mcp.onrender.com/mcp/
```

Primary 5-tool happy path:

1. `get_fhir_connection_status`
2. `list_follow_up_tasks`
3. `explain_result_decisions` for `synthetic-patient-003`
4. `generate_ai_follow_up_brief` for `synthetic-patient-003`
5. `create_follow_up_handoff_payload` for `synthetic-patient-003`

## Expected Results

- FHIR status reports `active_data_source: synthetic_fixture_data`.
- The task queue includes `synthetic-patient-003`.
- The potassium task is in `same_day_clinician_review_consideration`.
- Audit output explains the deterministic flagging decision.
- The AI brief includes structured evidence beside the narrative.
- In Gemini-enabled final demo mode, `fallback_used` should be `false`.
- The handoff payload reports `payload_only: true` and `ehr_write_performed: false`.

## Optional FHIR Feasibility Proof

Use `validate_fhir_context_connection` only if Prompt Opinion supplies
`X-FHIR-Server-URL`, `X-FHIR-Access-Token`, and `X-Patient-ID`, and the Render
service has `LIVE_FHIR_READS_ENABLED=true`.

The expected result is safe metadata only: reachability status, HTTP status,
resource type, and boolean token/context fields. The tool does not return tokens,
patient demographics, a full FHIR payload, or PHI-heavy data. The primary demo does
not require real PHI or live FHIR reads.

## Optional Second Case

Use `synthetic-patient-001` to show multiple unresolved findings:

- Hemoglobin A1c
- LDL cholesterol

The same patient also demonstrates suppression evidence for potassium.

## What Not To Claim

- Do not claim Aegis Follow-Up diagnoses, prescribes, treats, or recommends therapy.
- Do not claim live FHIR reads are the primary demo path.
- Do not claim real PHI is required.
- Do not claim an EHR write occurred.
- Do not claim a scheduling or care-coordination agent was actually contacted.
- Do not expose Gemini API keys, access tokens, screenshots with secrets, or PHI.

## Smoke Commands

Fallback mode:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --attempts 3 --delay-seconds 2 --timeout 30
```

Real Gemini mode, only after Render environment variables are configured:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --expect-real-llm
```

Live FHIR feasibility proof, only when a test FHIR server and temporary token are
configured operationally:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --expect-live-fhir --fhir-server-url https://example.fhir.test --fhir-access-token <token> --fhir-patient-id <patient-id>
```
