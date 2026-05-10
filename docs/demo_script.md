# Sprint 7 Demo Script

Goal: show Prompt Opinion or MCP Inspector discovering Follow-Up Radar, proving the
deterministic audit trail first, then showing controlled AI narrative synthesis from
the same structured evidence.

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
4. Show the registered tools, including `generate_ai_follow_up_brief`.
5. Call `list_follow_up_tasks` with the default primary care profile.
6. Show `synthetic-patient-003` in `same_day_clinician_review_consideration`.
7. Show `synthetic-patient-001` in `soon_clinician_review_consideration`.
8. Call `explain_result_decisions` for `synthetic-patient-001`.
9. Show flagged A1c and LDL decisions plus the suppressed potassium follow-up evidence.
10. Call `generate_ai_follow_up_brief` for `synthetic-patient-001`.
11. Show that `structured_findings`, `priority`, and `audit_summary` remain present
    beside the narrative.
12. Highlight `safety_validation`, `fallback_used`, and `fallback_reason`. In default
    Render mode, fallback is expected because no API key is configured.
13. Call `update_follow_up_task_status` for the synthetic-patient-003 potassium task with status `reviewed`.
14. Show `demo_state_only: true` and `ehr_write_performed: false`.
15. Call `get_ehr_integration_summary`.
16. Show `workflow_metrics`, including priority counts and demo status counts.
17. Close with: rules decide, AI synthesizes, safety validates, clinician remains in control.

## Sample Prompt Opinion Ask

Check this synthetic patient for unresolved abnormal results and draft a follow-up brief for clinician review.

Assess follow-up priority for synthetic-patient-003 and explain the deterministic rationale without adding clinical recommendations.

Assess follow-up priority for synthetic-patient-004.

List the follow-up task queue using the default primary care profile.

Explain why synthetic-patient-001 was flagged or suppressed.

Generate an AI follow-up brief for synthetic-patient-001 and show the deterministic evidence fields.

Mark task-synthetic-patient-003-obs-potassium-003-2026-04-24 as reviewed in the demo workflow.

Summarize the EHR integration model for this MCP server.

## Rehearsal Check

```bash
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/
```

Replace the URL with the deployed Render URL after the service is provisioned.
