# Sprint 2 Demo Script

Goal: show Prompt Opinion or MCP Inspector discovering Follow-Up Radar and producing a deterministic follow-up brief from synthetic FHIR data in under three minutes.

## Flow

1. Start or open the deployed server.
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
2. Open `/healthz`, `/readyz`, and `/version`.
3. Connect MCP Inspector or Prompt Opinion to `/mcp/`.
4. Show the five registered tools.
5. Call `find_unresolved_abnormal_results` for `synthetic-patient-001`.
6. Call `generate_follow_up_brief` for the same patient.
7. Show the brief findings, evidence, severity, and clinician review action.
8. Close with: Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Sample Prompt Opinion Ask

Check this synthetic patient for unresolved abnormal results and draft a follow-up brief for clinician review.

## Rehearsal Check

```bash
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/
```
