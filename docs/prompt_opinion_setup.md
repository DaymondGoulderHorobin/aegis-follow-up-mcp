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
4. Confirm tool discovery lists all five tools.
5. Invoke `get_patient_snapshot` for `synthetic-patient-001`.
6. Invoke `find_unresolved_abnormal_results` for `synthetic-patient-001`.
7. Invoke `generate_follow_up_brief` for `synthetic-patient-001`.
8. Record any initialization or timeout notes for demo rehearsal.

## Expected Tools

Prompt Opinion should discover:

- `get_patient_snapshot`
- `get_recent_observations`
- `find_unresolved_abnormal_results`
- `generate_follow_up_brief`
- `draft_clinician_note`

## Synthetic Fixture Mode

Sprint 3 defaults to synthetic fixture mode. If Prompt Opinion does not pass FHIR headers during early testing, the server still works against `synthetic-patient-001`.

If Prompt Opinion can pass context headers, the server accepts these case-insensitively:

- `X-FHIR-Server-URL`
- `X-FHIR-Access-Token`
- `X-Patient-ID`

`X-Patient-ID` can select a synthetic fixture patient. Access tokens are never returned, and helper output redacts token values.

## Demo Prompt

```text
Check synthetic-patient-001 for unresolved abnormal results and draft a follow-up brief for clinician review.
```

Expected behavior: unresolved A1c and LDL findings appear with evidence and clinician review actions. Potassium is not returned as unresolved because follow-up evidence exists in the synthetic fixture.

## Troubleshooting

- Failed initialization: confirm the URL ends in `/mcp/` and the server is awake.
- Missing tools: open `/version` and verify the deployed code is version `0.3.0`.
- Timeout: warm the deployment with `/healthz`, then retry initialization.
- Plain `GET /mcp` returns `406`: use MCP Inspector or Prompt Opinion instead of a browser GET.
- Wrong patient: pass `patient_id` as a tool argument, or pass `X-Patient-ID` when the client supports custom headers.
- Tool call failed: retry with fixture mode and `patient_id` set to `synthetic-patient-001`.
