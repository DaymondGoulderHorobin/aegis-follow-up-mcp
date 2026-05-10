# Final Demo Script

Goal: show Prompt Opinion or MCP Inspector discovering Follow-Up Radar, proving the
deterministic audit trail first, then showing controlled AI narrative synthesis from
the same structured evidence and a payload-only agent handoff.

Target deployed MCP URL:

```text
https://follow-up-radar-mcp.onrender.com/mcp/
```

## Flow

1. Open the deployed `/healthz`, `/readyz`, and `/version` endpoints.
2. Run or show the deployed smoke check:
   ```bash
   python scripts/smoke_mcp.py --url https://follow-up-radar-mcp.onrender.com/mcp/
   ```
3. Connect MCP Inspector or Prompt Opinion to `/mcp/`.
4. Show the registered tools, including `get_fhir_connection_status` and
   `create_follow_up_handoff_payload`.
5. Call `get_fhir_connection_status` and show `active_data_source: synthetic_fixture_data`.
6. Call `list_follow_up_tasks` with the default primary care profile.
7. Show `synthetic-patient-003` in `same_day_clinician_review_consideration`.
8. Show `synthetic-patient-001` in `soon_clinician_review_consideration`.
9. Call `explain_result_decisions` for `synthetic-patient-003`.
10. Show why potassium was flagged by deterministic rules.
11. Call `generate_ai_follow_up_brief` for `synthetic-patient-003`.
12. Show that `structured_findings`, `priority`, and `audit_summary` remain present
    beside the narrative.
13. Highlight `safety_validation`, `fallback_used`, and `fallback_reason`. In default
    Render mode, fallback is expected because no API key is configured.
14. Call `create_follow_up_handoff_payload` for `synthetic-patient-003`.
15. Show `payload_only: true`, `required_human_review: true`, and
    `ehr_write_performed: false`.
16. Call `update_follow_up_task_status` for the synthetic-patient-003 potassium task with status `reviewed`.
17. Show `demo_state_only: true` and `ehr_write_performed: false`.
18. Call `get_ehr_integration_summary`.
19. Show `workflow_metrics`, including priority counts and demo status counts.
20. Close with: rules decide, AI synthesizes, audit trail explains, handoff payload integrates, clinician remains in control.

## Sample Prompt Opinion Ask

Check this synthetic patient for unresolved abnormal results and draft a follow-up brief for clinician review.

Assess follow-up priority for synthetic-patient-003 and explain the deterministic rationale without adding clinical recommendations.

Assess follow-up priority for synthetic-patient-004.

List the follow-up task queue using the default primary care profile.

Explain why synthetic-patient-001 was flagged or suppressed.

Show the FHIR connection status for this demo.

Generate an AI follow-up brief for synthetic-patient-001 and show the deterministic evidence fields.

Create a follow-up handoff payload for synthetic-patient-003 without sending it anywhere.

Mark task-synthetic-patient-003-obs-potassium-003-2026-04-24 as reviewed in the demo workflow.

Summarize the EHR integration model for this MCP server.

## Rehearsal Check

```bash
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/
```

Replace the URL with the deployed Render URL after the service is provisioned.
