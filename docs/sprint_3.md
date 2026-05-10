# Sprint 3

## Objective

Deploy Follow-Up Radar MCP to a public HTTPS endpoint and validate that MCP Inspector and Prompt Opinion can initialize the server, discover tools, and invoke deterministic synthetic outputs.

## Branch

```text
codex/sprint-3-deployment-validation
```

## Deployment Target

Recommended target: Render Web Service with Docker.

The repository includes:

- `Dockerfile`
- `render.yaml`
- `/healthz`, `/readyz`, `/version`, and `/mcp/`
- `scripts/smoke_mcp.py`

Expected deployed base URL:

```text
https://follow-up-radar-mcp.onrender.com
```

If Render assigns a different subdomain, use the actual Render URL in every check below.

## Public Endpoint Checks

```bash
curl https://follow-up-radar-mcp.onrender.com/healthz
curl https://follow-up-radar-mcp.onrender.com/readyz
curl https://follow-up-radar-mcp.onrender.com/version
python scripts/smoke_mcp.py --url https://follow-up-radar-mcp.onrender.com/mcp/
```

Expected smoke result:

- MCP connection initializes.
- All five tools are listed.
- `find_unresolved_abnormal_results` returns Hemoglobin A1c and LDL cholesterol.
- `generate_follow_up_brief` includes the safety disclaimer.

## MCP Inspector Validation

1. Start MCP Inspector.
2. Select streamable HTTP transport.
3. Use `https://follow-up-radar-mcp.onrender.com/mcp/`.
4. Initialize.
5. List tools.
6. Call `get_patient_snapshot`.
7. Call `find_unresolved_abnormal_results`.
8. Call `generate_follow_up_brief`.
9. Confirm deterministic synthetic output and the safety disclaimer.

## Prompt Opinion Validation

1. Add the deployed MCP server URL in Prompt Opinion.
2. Confirm all five tools are discovered.
3. Run:
   ```text
   Check this synthetic patient for unresolved abnormal results and draft a follow-up brief for clinician review.
   ```
4. Confirm Prompt Opinion can invoke the deterministic tool path.
5. Record any initialization delays, missing headers, or timeout notes.

## Known Risks

- A public Render deployment has not been provisioned from this local environment.
- Free Render services can cold start, so the smoke script includes retry settings.
- `GET /mcp/` may return an MCP-specific error or `406`; use an MCP client for validation.
- Prompt Opinion header forwarding may vary during early testing.

## Safety

- Synthetic data only.
- No PHI.
- No real FHIR tokens.
- No diagnosis or treatment directives.
- All generated output remains clinical decision support for clinician review.

## Sprint 4

Sprint 4 advertises Prompt Opinion FHIR-context MCP extension support while keeping the server deterministic and synthetic-data only.
