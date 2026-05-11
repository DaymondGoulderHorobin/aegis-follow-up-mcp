# Sprint 5

## Objective

Expand the deployed Prompt Opinion MCP demo with deterministic multi-patient triage and stronger clinician-facing output safety controls.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Branch

```text
codex/sprint-5-deterministic-triage
```

## Multi-Patient Fixture Scenarios

- `synthetic-patient-001`: existing unresolved A1c and LDL case; potassium remains suppressed by follow-up evidence.
- `synthetic-patient-003`: high potassium without follow-up evidence; expected priority is `same_day_clinician_review_consideration`.
- `synthetic-patient-004`: clean chart with normal observations; expected priority is `no_unresolved_abnormal_result_found`.
- `synthetic-patient-005`: abnormal A1c with follow-up evidence; expected priority is `no_unresolved_abnormal_result_found`.

## Deterministic Priority Tool

Sprint 5 adds `assess_follow_up_priority`.

The tool returns:

- `disclaimer`
- `patient_id`
- `priority_tier`
- `summary`
- `rationale`
- `findings`
- `suggested_clinician_review_actions`

Allowed priority tiers:

- `same_day_clinician_review_consideration`
- `soon_clinician_review_consideration`
- `routine_clinician_review`
- `no_unresolved_abnormal_result_found`

The tool reuses deterministic unresolved-abnormal-result detection and does not add diagnosis, prescribing, treatment-plan, therapy recommendation, or medication-adjustment language.

## Safety Hardening

Clinician-facing text is checked for disallowed recommendation phrases such as:

- `diagnosed with`
- `prescribe`
- `start treatment`
- `must treat`
- `should start`
- `medication adjustment`
- `lipid-lowering therapy`
- `therapy may be warranted`

Outputs include the shared disclaimer and use neutral review wording.

## Validation

Run locally:

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/ --attempts 2 --delay-seconds 1 --timeout 20
```

After merge and Render deploy:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --attempts 3 --delay-seconds 2 --timeout 30
```

Then refresh Prompt Opinion MCP tool discovery and confirm `assess_follow_up_priority` appears.

## Safety Boundaries

- Synthetic data only.
- No PHI.
- No real FHIR reads.
- No LLM summarisation.
- No refresh tokens.
- No `offline_access`.
- No diagnosis or treatment directives.
