# Security Policy

## Supported Posture

Aegis Follow-Up currently supports a synthetic-data demo and product-foundation
pilot planning posture. The public demo is not a production clinical deployment
and must not be connected to real PHI without customer-governed security,
privacy, and clinical review.

Environment expectations:

- `local`: developer testing with synthetic fixtures.
- `demo`: Prompt Opinion marketplace demo with synthetic fixtures and no PHI.
- `staging`: controlled internal validation with managed secrets and read-only
  sandbox FHIR where approved.
- `pilot`: customer-approved, authenticated, read-only clinical pilot posture.
- `production`: future work, not claimed by the current repository.

## Secrets Policy

- Never commit API keys, FHIR access tokens, refresh tokens, authorization
  headers, session cookies, or customer credentials.
- Use environment variables or managed secret storage for operational secrets.
- Keep `GEMINI_API_KEY` blank in `.env.example`.
- Do not put secrets in screenshots, demo recordings, prompts, issue comments, or
  logs.

## FHIR Token Policy

FHIR access tokens are runtime-only values. The server may inspect token presence
to prove context is available, but token values must not be logged, returned,
stored, or displayed.

The demo does not request `offline_access` and does not implement refresh-token
support.

## PHI-Safe Logging

- Do not log raw FHIR payloads.
- Do not log patient names, identifiers, contact details, addresses, notes, or
  full observation payloads from live systems.
- Do not log authorization headers or `X-FHIR-Access-Token`.
- Prefer structured event names, booleans, counts, synthetic patient IDs, and
  non-sensitive status codes.
- Use redaction helpers before writing any diagnostic header output.
- Use `app.safety.logging.build_safe_log_event` for future structured log
  metadata so token-like fields are redacted and payload-shaped values are
  omitted.

## Dependency And Validation Checks

Before deployment or PR review, run:

```bash
pytest
ruff check .
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/
```

For remote fallback validation:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --attempts 3 --delay-seconds 2 --timeout 30
```

Dependency review should be repeated before pilot use and whenever core web,
MCP, HTTP, or AI dependencies change.

## Vulnerability Reporting

Use public GitHub issues only for non-sensitive documentation or reproducible
demo bugs that contain no secrets and no PHI.

For sensitive security issues, do not include credentials, tokens, screenshots,
or patient data in public issues. Use a private maintainer contact or a private
security advisory channel before sharing details.

## Production Warning

The public demo authentication posture is not acceptable for real PHI or clinical
operations. A production or pilot deployment requires authentication, tenant
isolation, PHI-safe logging, monitoring, access review, incident response, and
customer-specific legal/security review.
