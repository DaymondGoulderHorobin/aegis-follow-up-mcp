# Sprint 1

## Goals

- Create a clean Python 3.11+ repository.
- Scaffold a FastMCP-first server with health endpoints.
- Add safe synthetic FHIR fixture mode.
- Expose or scaffold the first five MCP tools.
- Add tests, Docker support, CI, and operator documentation.

## What Was Built

- FastAPI health endpoints: `/healthz`, `/readyz`, `/version`.
- MCP endpoint path: `/mcp`.
- FastMCP tool registration with a local metadata fallback when FastMCP is unavailable.
- Synthetic FHIR bundle with patient, conditions, medication, encounter, observations, and follow-up evidence.
- Deterministic abnormal result detection.
- Template-based clinician follow-up brief generation.
- Clinician note draft output that stays framed for review.
- Pytest tests and GitHub Actions workflow.

## Sprint 2

- Confirm Prompt Opinion MCP transport compatibility.
- Run MCP Inspector against the server.
- Deploy to a public HTTPS endpoint.
- Connect the deployed endpoint to Prompt Opinion.
- Add optional LLM summarisation behind the deterministic brief interface.
- Prepare marketplace details and final demo assets.

## Known Risks

- The FastMCP HTTP mounting API can differ by package version, so Sprint 2 should validate the exact runtime transport.
- External FHIR mode is scaffolded only and should be hardened before use with real integrations.
- The current fixture is intentionally small and should not be treated as clinical validation.
