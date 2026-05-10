# Sprint 8

## Objective

Final integration polish: make the MCP judge-ready by clarifying fixture versus
live FHIR behavior, adding agent instructions, exposing a payload-only handoff
schema, and hardening edge cases.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Branch

```text
codex/sprint-8-final-integration-polish
```

## New Tools

Sprint 8 adds:

- `get_fhir_connection_status`
- `create_follow_up_handoff_payload`

`get_fhir_connection_status` reports whether FHIR-context headers are present,
whether live FHIR reads are enabled, and which data source is active. It never
returns access-token values.

`create_follow_up_handoff_payload` returns a structured handoff payload for future
scheduling, care-coordination, or EHR-task agents. It does not send the payload,
contact another agent, or write to an EHR.

## Edge-Case Hardening

Tests cover:

- unknown patient IDs
- observations missing `valueQuantity`
- observations missing reference ranges
- malformed observation dates
- follow-up evidence without dates
- invalid rule profiles
- invalid workflow statuses
- clean patients with no handoff task
- FHIR status token non-disclosure

## Validation

Run locally:

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/ --attempts 2 --delay-seconds 1 --timeout 30
```

After merge and Render redeploy:

```bash
python scripts/smoke_mcp.py --url https://follow-up-radar-mcp.onrender.com/mcp/ --attempts 3 --delay-seconds 2 --timeout 30
```

If Gemini mode is configured on Render:

```bash
python scripts/smoke_mcp.py --url https://follow-up-radar-mcp.onrender.com/mcp/ --expect-real-llm
```

## Deferred Production Items

- Full A2A transport.
- Real external FHIR reads as the primary path.
- Real EHR writes.
- Persistent workflow database.
- Scheduling integration.
- Additional LLM tools beyond the controlled AI narrative path.

## Safety Boundaries

- Synthetic data remains the default path.
- No PHI is committed, logged, or required for the demo.
- No real EHR writes.
- No autonomous task dispatch.
- No new broad FHIR scopes.
- No `offline_access`.
- No refresh-token support.
- AI output remains optional, safety-validated, and unable to override deterministic findings.
- Handoff payload is schema/demo output only.
