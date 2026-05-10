# Deployment

Recommended target: Render Web Service using the Dockerfile and `render.yaml`.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

Current deployment status: public Render URL is provisioned for testing.

Expected deployed base URL:

```text
https://follow-up-radar-mcp.onrender.com
```

Expected MCP URL:

```text
https://follow-up-radar-mcp.onrender.com/mcp/
```

## Required Environment

```text
APP_ENV=production
LOG_LEVEL=INFO
FIXTURE_MODE=true
FHIR_SYNTHETIC_BUNDLE_PATH=data/synthetic_patient_bundle.json
HOST=0.0.0.0
PORT=8000
MCP_TRANSPORT=streamable-http
MCP_JSON_RESPONSE=false
MCP_STATELESS_HTTP=false
ALLOWED_ORIGINS=
```

Keep `FIXTURE_MODE=true` for the demo. Do not configure real FHIR credentials in the deployment.

## Render Blueprint Setup

1. In Render, create a new Blueprint from `DaymondGoulderHorobin/follow-up-radar-mcp`.
2. Select `render.yaml` from the repository root.
3. Confirm the service uses Docker runtime.
4. Confirm `healthCheckPath` is `/healthz`.
5. Confirm `FIXTURE_MODE=true`.
6. Apply the Blueprint and wait for the first deploy.

The Blueprint is intentionally synthetic-only and does not include FHIR tokens or secrets.

Render references:

- [Blueprint YAML Reference](https://render.com/docs/blueprint-spec)
- [Docker on Render](https://render.com/docs/docker)
- [Health Checks](https://render.com/docs/health-checks)

## Manual Render Setup

Use this if the Blueprint path is not available:

1. Create a new Render Web Service from the GitHub repository.
2. Choose Docker as the runtime.
3. Use branch `main` after Sprint 3 merges, or `codex/sprint-3-deployment-validation` for branch validation.
4. Set the health check path to `/healthz`.
5. Set the environment variables listed above.
6. Deploy the service.

## Smoke Checks

Health:

```bash
curl https://follow-up-radar-mcp.onrender.com/healthz
curl https://follow-up-radar-mcp.onrender.com/readyz
curl https://follow-up-radar-mcp.onrender.com/version
```

MCP:

```bash
python scripts/smoke_mcp.py --url https://follow-up-radar-mcp.onrender.com/mcp/
```

For Sprint 4, the smoke script also validates that MCP initialize capabilities include `ai.promptopinion/fhir-context` with optional scopes and no `offline_access`.

For Sprint 5, the smoke script also validates the sixth tool, `assess_follow_up_priority`, against the critical synthetic potassium case.

If `GET /mcp` returns `406`, that does not by itself mean the MCP endpoint is broken. Use an MCP client, MCP Inspector, or the smoke script.

## Prompt Opinion FHIR Context

The deployed demo advertises Prompt Opinion FHIR-context compatibility, but it does not require real FHIR secrets. Users can leave the trust toggle disabled and still run the synthetic fixture workflow.

If Prompt Opinion sends context after a user grants optional scopes, the app accepts:

```text
X-FHIR-Server-URL
X-FHIR-Access-Token
X-Patient-ID
```

Tokens are not logged or returned. The app does not request `offline_access`, does not receive refresh tokens, and does not call an external FHIR server.

## Docker

Local build:

```bash
docker build -t follow-up-radar-mcp .
docker run --rm -p 8000:8000 follow-up-radar-mcp
```

CI runs `docker build -t follow-up-radar-mcp .` on pull requests.
