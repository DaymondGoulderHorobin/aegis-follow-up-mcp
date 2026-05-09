# Sprint 3 Demo Script

Goal: show Prompt Opinion or MCP Inspector discovering Follow-Up Radar and producing a deterministic follow-up brief from synthetic FHIR data in under three minutes.

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
4. Show the five registered tools.
5. Call `find_unresolved_abnormal_results` for `synthetic-patient-001`.
6. Call `generate_follow_up_brief` for the same patient.
7. Show the A1c and LDL findings, evidence, severity, and clinician review action.
8. Point out that potassium is excluded because deterministic follow-up evidence exists.
9. Close with: Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Sample Prompt Opinion Ask

Check this synthetic patient for unresolved abnormal results and draft a follow-up brief for clinician review.

## Rehearsal Check

```bash
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/
```

Replace the URL with the deployed Render URL after the service is provisioned.
