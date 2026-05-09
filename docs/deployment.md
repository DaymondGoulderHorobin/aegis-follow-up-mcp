# Deployment

Recommended Sprint 2 target: Render Web Service using the Dockerfile.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

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

Keep `FIXTURE_MODE=true` for the Sprint 2 demo. Do not configure real FHIR credentials in the deployment.

## Render Setup

1. Create a new Render Web Service from the GitHub repository.
2. Choose Docker as the runtime.
3. Set the environment variables above. Render also supplies `PORT`; the Dockerfile respects it.
4. Deploy the service.
5. Confirm these endpoints:
   - `https://<service>.onrender.com/healthz`
   - `https://<service>.onrender.com/readyz`
   - `https://<service>.onrender.com/version`
   - `https://<service>.onrender.com/mcp/`

## Smoke Checks

Health:

```bash
curl https://<service>.onrender.com/healthz
curl https://<service>.onrender.com/readyz
curl https://<service>.onrender.com/version
```

MCP:

```bash
python scripts/smoke_mcp.py --url https://<service>.onrender.com/mcp/
```

If `GET /mcp` returns `406`, that does not by itself mean the MCP endpoint is broken. Use an MCP client, MCP Inspector, or the smoke script.

## Docker

Local build:

```bash
docker build -t follow-up-radar-mcp .
docker run --rm -p 8000:8000 follow-up-radar-mcp
```

CI runs `docker build -t follow-up-radar-mcp .` on pull requests.
