# Sprint 6

## Objective

Add a product workflow layer that makes Aegis Follow-Up feel like an integration-ready clinical operations component while staying deterministic, synthetic-data only, and clinician-review focused.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Branch

```text
codex/sprint-6-product-workflow-layer
```

## Workflow Tools

Sprint 6 adds:

- `list_rule_profiles`
- `explain_result_decisions`
- `list_follow_up_tasks`
- `update_follow_up_task_status`
- `get_ehr_integration_summary`

The existing tools remain available.

## Product Layer

- Audit trail decisions explain flagged and suppressed observations with rule IDs, evidence, and follow-up suppression details.
- Static rule profiles demonstrate deterministic workflow configurability for primary care, metabolic, cardiovascular, and safety-critical lab review.
- The task queue groups unresolved findings by clinician-review priority across synthetic patients.
- Demo workflow state records reviewed, follow-up documented, or dismissed states in memory only.
- The EHR integration summary describes FHIR context in and clinician-reviewed task or note out.

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

Then refresh Prompt Opinion MCP tool discovery and confirm the Sprint 6 tools appear.

## Known Risks And Deferred Work

- Demo workflow state is in-memory and intentionally not production persistence.
- Rule profiles are static JSON fixtures and do not include an admin UI.
- EHR write targets are a future integration story only.
- Real FHIR reads, refresh tokens, and LLM summarisation remain deferred.

## Safety Boundaries

- Synthetic data only.
- No PHI.
- No real EHR writes.
- No real FHIR reads.
- No refresh tokens.
- No `offline_access`.
- No LLM summarisation.
- No autonomous clinical actions.
