# Codex Development Guide

This guide gives future Codex sessions clear boundaries for extending Aegis
Follow-Up.

## Core Rule

Preserve the synthetic demo path and clinical safety posture. Do not add live EHR
writes, autonomous clinical actions, diagnosis, prescribing, therapy, treatment
recommendations, real PHI, real tokens, or mandatory external secrets.

## Current Product Shape

- FastAPI service with FastMCP tool registration.
- Synthetic FHIR fixtures by default.
- Streamable HTTP MCP endpoint for Prompt Opinion.
- Optional Gemini narrative mode with deterministic fallback.
- Optional read-only FHIR connectivity proof.
- No persistent clinical workflow database.
- No autonomous EHR writeback.

## Safe Areas To Edit

- Documentation and runbooks.
- Synthetic fixtures, when clearly non-PHI.
- Deterministic rule tests.
- Safety validation tests.
- Prompt Opinion setup docs.
- Environment profile docs.
- Non-sensitive observability helpers.
- Safe structured logging helpers that redact tokens and omit payload-shaped
  values.

## High-Risk Areas

Treat these as requiring explicit user approval and extra tests:

- FHIR ingestion beyond the connectivity proof.
- Any EHR writeback.
- Authentication or tenanting changes.
- LLM prompt changes that affect clinical wording.
- Safety validation changes.
- Environment variable defaults.
- Render deployment behavior.

## Required Commands

Before finishing a code or documentation sprint, run:

```bash
pytest
ruff check .
git diff --check
```

When MCP behavior or docs around tools change, also run:

```bash
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/
```

Start a local server first:

```bash
uvicorn app.main:app --reload --port 8000
```

## Branch And PR Protocol

- Branch from current `main` unless intentionally stacking on an unmerged PR.
- Use the `codex/` branch prefix.
- Keep PRs small and reviewable.
- State whether runtime behavior changed.
- State safety and validation results.
- Never include secrets, PHI, real tokens, or screenshots with sensitive data.

## Testing Guidance

Tests should protect:

- health, readiness, and version endpoints;
- MCP tool registration;
- Prompt Opinion FHIR-context extension;
- synthetic fixture default behavior;
- safety wording and prohibited claims;
- token redaction and no full FHIR payload exposure;
- PHI-safe structured logging helpers;
- docs presence for product-foundation guardrails.

## Documentation Voice

Use consistent language:

- clinical decision support only;
- for clinician review;
- not a diagnosis or treatment directive;
- synthetic fixture demo by default;
- optional Gemini synthesis;
- optional FHIR reachability proof;
- no autonomous EHR write.

Avoid claims of production readiness, clinical validation, autonomous care
coordination, diagnosis, prescribing, or treatment recommendations.
