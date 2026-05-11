# Aegis Follow-Up Final Demo Script

Goal: show a focused, judge-friendly flow that proves transparency, deterministic
clinical logic, controlled AI synthesis, and handoff readiness without claiming
live FHIR reads or EHR writes.

Target deployed MCP URL:

```text
https://aegis-follow-up-mcp.onrender.com/mcp/
```

## Five-Step Flow

1. **FHIR Transparency**
   Call `get_fhir_connection_status` and show:
   - `active_data_source: synthetic_fixture_data`
   - `live_fhir_reads_enabled: false`
   - no PHI required for the demo

2. **Clinic Queue**
   Call `list_follow_up_tasks` with `default_primary_care`.
   Show `synthetic-patient-003` in `same_day_clinician_review_consideration`.

3. **Deterministic Audit And Priority**
   Call `explain_result_decisions` and `assess_follow_up_priority` for
   `synthetic-patient-003`. Show that potassium was flagged by deterministic rules,
   not by the LLM.

4. **Controlled AI Narrative**
   Call `generate_ai_follow_up_brief` for `synthetic-patient-003`. Show:
   - `structured_findings`
   - `priority`
   - `audit_summary`
   - `safety_validation`
   - `fallback_used`

   In final Gemini mode, confirm `fallback_used: false`. In fallback mode, explain
   that the demo still works without an API key.

5. **Agent-Ecosystem Handoff**
   Call `create_follow_up_handoff_payload` for `synthetic-patient-003`. Show:
   - `payload_only: true`
   - `required_human_review: true`
   - `ehr_write_performed: false`
   - `outbound_action_performed: false`

Close with: Prompt Opinion chooses tools, Aegis Follow-Up rules decide, Gemini
synthesizes, safety validates, the audit trail explains, and clinician review
remains in control.

## Optional Mini-Case

If time allows, call `explain_result_decisions` for `synthetic-patient-001` to show
multiple unresolved findings: Hemoglobin A1c and LDL cholesterol. Also point out
that potassium was suppressed because the synthetic fixture includes follow-up
evidence.

## Demo Prompts

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

## Rehearsal Checks

Fallback mode:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --attempts 3 --delay-seconds 2 --timeout 30
```

Gemini mode, only after Render secrets are configured:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --expect-real-llm
```
