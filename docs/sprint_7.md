# Sprint 7

## Objective

Add a controlled AI narrative layer while keeping deterministic review as the
clinical source of truth.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Branch

```text
codex/sprint-7-ai-narrative-layer
```

## New Tool

Sprint 7 adds:

- `generate_ai_follow_up_brief`

The tool accepts `patient_id` and `profile_id`, gathers deterministic source data,
and returns a concise narrative with the structured evidence still included.

## Guardrails

- LLM provider mode defaults to `disabled`.
- Gemini can be enabled with Render environment variables only.
- Missing keys, provider errors, timeouts, malformed responses, or unsafe wording
  return deterministic fallback output.
- The LLM cannot change priority, structured findings, audit counts, task status, or
  follow-up evidence.
- Disallowed wording is blocked and unsafe model text is not returned.

## Dynamic Workflow Metrics

`get_ehr_integration_summary` now includes:

- total current synthetic follow-up tasks
- task counts by priority tier
- demo workflow status counts for open, reviewed, follow-up documented, and dismissed

The summary continues to return `demo_state_only: true` and `ehr_write_performed: false`.

## Validation

Run locally:

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/ --attempts 2 --delay-seconds 1 --timeout 20
```

After merge and Render redeploy:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --attempts 3 --delay-seconds 2 --timeout 30
```

If Gemini mode is configured on Render:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --expect-real-llm
```

## Safety Boundaries

- Synthetic data only.
- No PHI.
- No real EHR writes.
- No real FHIR reads.
- No refresh tokens.
- No `offline_access`.
- No committed API keys.
- No autonomous clinical actions.
- AI output is clinician-review narrative only.
