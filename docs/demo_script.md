# Sprint 1 Demo Script

Goal: show Follow-Up Radar finding potentially unresolved abnormal results from synthetic FHIR data in under three minutes.

## Flow

1. Start the server.
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
2. Open `/healthz`, `/readyz`, and `/version`.
3. Open `/mcp` and show the five registered tool names.
4. Invoke `find_unresolved_abnormal_results` with fixture mode.
5. Invoke `generate_follow_up_brief`.
6. Show the brief findings, evidence, severity, and clinician review action.
7. Close with: synthetic data only, clinical decision support only, for clinician review.

## Sample Prompt Opinion Ask

Check this synthetic patient for unresolved abnormal results and draft a follow-up brief for clinician review.
