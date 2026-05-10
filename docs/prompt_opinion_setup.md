# Prompt Opinion Setup

Use the deployed `/mcp/` endpoint as a remote MCP server.

## Server URL

```text
https://follow-up-radar-mcp.onrender.com/mcp/
```

The final URL should be replaced with the actual Render service URL if Render assigns a different subdomain. Use the trailing slash if the client asks for an exact URL.

## Setup Checklist

1. Verify `/healthz`, `/readyz`, and `/version` in a browser.
2. Run:
   ```bash
   python scripts/smoke_mcp.py --url https://follow-up-radar-mcp.onrender.com/mcp/
   ```
3. Open Prompt Opinion and add the MCP server URL.
4. Continue through initialization so Prompt Opinion can inspect capabilities.
5. Confirm tool discovery lists the final workflow, FHIR transparency, handoff, and AI narrative tools.
6. Confirm the FHIR-context trust or extension toggle appears.
7. Confirm all requested scopes are optional.
8. Invoke `get_patient_snapshot` for `synthetic-patient-001`.
9. Invoke `find_unresolved_abnormal_results` for `synthetic-patient-001`.
10. Invoke `generate_follow_up_brief` for `synthetic-patient-001`.
11. Invoke `assess_follow_up_priority` for `synthetic-patient-003`.
12. Invoke `assess_follow_up_priority` for `synthetic-patient-004`.
13. Invoke `list_follow_up_tasks` with the default profile.
14. Invoke `explain_result_decisions` for `synthetic-patient-001`.
15. Invoke `generate_ai_follow_up_brief` for `synthetic-patient-001`.
16. Invoke `get_fhir_connection_status`.
17. Invoke `create_follow_up_handoff_payload` for `synthetic-patient-003`.
18. Invoke `update_follow_up_task_status` for a demo task.
19. Invoke `get_ehr_integration_summary`.
20. Record any initialization, trust-toggle, header-forwarding, or timeout notes for demo rehearsal.

## FHIR-Context Extension

Sprint 4 advertises Prompt Opinion's documented MCP extension during initialize:

```text
capabilities.extensions.ai.promptopinion/fhir-context
```

Requested scopes:

- `patient/Patient.rs`
- `patient/Observation.rs`
- `patient/Condition.rs`
- `patient/MedicationStatement.rs`
- `patient/Encounter.rs`

All scopes are optional by default. Users can leave the extension disabled and still use the deterministic synthetic demo. The server does not request `offline_access`, does not receive refresh tokens, and does not perform real external FHIR reads.

## Expected Tools

Prompt Opinion should discover:

- `get_patient_snapshot`
- `get_recent_observations`
- `find_unresolved_abnormal_results`
- `generate_follow_up_brief`
- `generate_ai_follow_up_brief`
- `draft_clinician_note`
- `assess_follow_up_priority`
- `list_rule_profiles`
- `explain_result_decisions`
- `list_follow_up_tasks`
- `get_fhir_connection_status`
- `create_follow_up_handoff_payload`
- `update_follow_up_task_status`
- `get_ehr_integration_summary`

## Synthetic Fixture Mode

Sprint 8 defaults to synthetic fixture mode and LLM fallback mode. If Prompt Opinion does not pass FHIR headers during testing, the server still works against these fixture patients:

- `synthetic-patient-001`: unresolved A1c and LDL.
- `synthetic-patient-003`: high potassium priority case.
- `synthetic-patient-004`: clean chart case.
- `synthetic-patient-005`: abnormal A1c suppressed by follow-up evidence.

If a user trusts the server and authorizes FHIR context, Prompt Opinion may pass these headers. The server accepts them case-insensitively:

- `X-FHIR-Server-URL`
- `X-FHIR-Access-Token`
- `X-Patient-ID`

`X-Patient-ID` can select a synthetic fixture patient. Access tokens are never returned, and helper output redacts token values.

Use `get_fhir_connection_status` when anyone asks whether the demo is fixture-backed
or connected to a live FHIR server. The expected deployed demo source is
`synthetic_fixture_data`.

## Demo Prompt

```text
Check synthetic-patient-001 for unresolved abnormal results and draft a follow-up brief for clinician review.
```

Expected behavior: unresolved A1c and LDL findings appear with evidence and clinician review actions. Potassium is not returned as unresolved because follow-up evidence exists in the synthetic fixture.

```text
Generate an AI follow-up brief for synthetic-patient-001 and show the deterministic evidence fields.
```

Expected behavior: the response includes narrative plus `structured_findings`,
`priority`, `audit_summary`, `safety_validation`, and fallback metadata. In default
Render mode, deterministic fallback is expected because no Gemini key is configured.

```text
Create a follow-up handoff payload for synthetic-patient-003 without sending it anywhere.
```

Expected behavior: the response includes `payload_only: true`,
`required_human_review: true`, and `ehr_write_performed: false`.

## BYO Agent Safety Instructions

Use the full instruction block in `docs/prompt_opinion_agent_instructions.md`, or a
short Prompt Opinion BYO agent instruction such as:

```text
Use Follow-Up Radar MCP tool output as clinical decision support only. Do not add diagnosis, prescribing, treatment-plan, therapy recommendation, medication-adjustment, or urgency instructions beyond the deterministic MCP output. Preserve the disclaimer and ask for clinician review.
```

The server itself validates clinician-facing text for disallowed recommendation phrases, but the BYO agent should still be instructed not to embellish tool results.

## Workflow Demo Prompts

```text
List the follow-up task queue using the default primary care profile.
```

```text
Explain why synthetic-patient-001 was flagged or suppressed.
```

```text
Mark task-synthetic-patient-003-obs-potassium-003-2026-04-24 as reviewed in the demo workflow and confirm whether any EHR write was performed.
```

```text
Summarize the EHR integration model for Follow-Up Radar.
```

```text
Show the FHIR connection status and explain whether live FHIR reads occurred.
```

```text
Create a payload-only follow-up handoff for synthetic-patient-003.
```

## Troubleshooting

- Failed initialization: confirm the URL ends in `/mcp/` and the server is awake.
- Missing FHIR-context toggle: run the smoke script and confirm initialize capabilities include `ai.promptopinion/fhir-context`.
- Missing tools: open `/version` and verify the deployed code is version `0.8.0`.
- Timeout: warm the deployment with `/healthz`, then retry initialization.
- Plain `GET /mcp` returns `406`: use MCP Inspector or Prompt Opinion instead of a browser GET.
- Wrong patient: pass `patient_id` as a tool argument, or pass `X-Patient-ID` when the client supports custom headers.
- Tool call failed: retry with fixture mode and `patient_id` set to `synthetic-patient-001`.
