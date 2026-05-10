# Follow-Up Radar MCP

Follow-Up Radar is a clinician-facing MCP server that reviews synthetic FHIR patient data for potentially unresolved abnormal results and generates a structured follow-up brief for clinician review.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Hackathon Positioning

- Project: Agents Assemble Prompt Opinion Hackathon
- Protocol: MCP server first
- Data mode: synthetic FHIR fixtures only
- Target MCP endpoint: `/mcp/`
- Health endpoints: `/healthz`, `/readyz`, `/version`
- Current version: `0.7.0`

## Local Setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Then open:

- `http://localhost:8000/healthz`
- `http://localhost:8000/readyz`
- `http://localhost:8000/version`
- `http://localhost:8000/mcp/`

## Test

```bash
pytest
ruff check .
```

## Docker

```bash
docker build -t follow-up-radar-mcp .
docker run --rm -p 8000:8000 follow-up-radar-mcp
```

## Deployment

The project includes Render Blueprint configuration in `render.yaml`.

Expected deployed MCP URL after provisioning:

```text
https://follow-up-radar-mcp.onrender.com/mcp/
```

Validate a deployed endpoint with:

```bash
python scripts/smoke_mcp.py --url https://follow-up-radar-mcp.onrender.com/mcp/
```

## MCP Tool Notes

The server exposes these MCP tools:

- `get_patient_snapshot`
- `get_recent_observations`
- `find_unresolved_abnormal_results`
- `generate_follow_up_brief`
- `generate_ai_follow_up_brief`
- `draft_clinician_note`
- `assess_follow_up_priority`
- `list_rule_profiles`
- `explain_result_decisions`
- `list_follow_up_tasks`
- `update_follow_up_task_status`
- `get_ehr_integration_summary`

The code registers these tools with FastMCP when the `fastmcp` package is installed. In local fixture-only test environments without FastMCP, `/mcp` returns tool metadata so the rest of the project remains testable.

`assess_follow_up_priority` returns deterministic clinician-review priority tiers:

- `same_day_clinician_review_consideration`
- `soon_clinician_review_consideration`
- `routine_clinician_review`
- `no_unresolved_abnormal_result_found`

It does not return diagnosis, prescribing, treatment-plan, or medication-adjustment instructions.

Sprint 6 adds a product workflow layer:

- audit trail decisions that explain flagged and suppressed results
- static deterministic rule profiles for clinic workflow tuning
- a priority-grouped follow-up task queue
- simulated clinician review state with no EHR write
- an EHR integration summary for FHIR-in and clinician-reviewed task or note out

Sprint 7 adds a controlled AI narrative layer:

- deterministic findings, priorities, audit counts, and task context remain the source of truth
- optional Gemini synthesis can create a concise clinician-review narrative
- disabled or missing LLM configuration returns deterministic fallback output
- unsafe model wording is blocked and replaced with deterministic fallback text
- the AI response always includes structured evidence beside the narrative

For MCP Inspector and deployment guidance, see:

- `docs/mcp_inspector.md`
- `docs/deployment.md`
- `docs/prompt_opinion_setup.md`
- `docs/commercial_workflow.md`

## Prompt Opinion Integration Notes

The server stays MCP-first and deterministic at its clinical decision boundary. Sprint 4
advertises Prompt Opinion's FHIR-context MCP extension during initialize:

```text
capabilities.extensions.ai.promptopinion/fhir-context
```

Requested SMART scopes are optional by default:

- `patient/Patient.rs`
- `patient/Observation.rs`
- `patient/Condition.rs`
- `patient/MedicationStatement.rs`
- `patient/Encounter.rs`

The server does not request `offline_access`, does not handle refresh tokens, and does
not fetch real FHIR data. The optional Sprint 7 LLM path only synthesizes narrative
from deterministic structured output.

If a Prompt Opinion user trusts the server and authorizes FHIR context, these headers may be sent to tool calls:

- `X-FHIR-Server-URL`
- `X-FHIR-Access-Token`
- `X-Patient-ID`

If any required context is missing, the app uses fixture mode.

## Synthetic Data And Safety

The included fixture data is synthetic and intentionally small for a reliable hackathon demo. It includes multiple synthetic outcomes:

- `synthetic-patient-001`: unresolved A1c and LDL, with potassium suppressed by follow-up evidence.
- `synthetic-patient-003`: high potassium without follow-up evidence for priority triage testing.
- `synthetic-patient-004`: clean chart with no unresolved abnormal results.
- `synthetic-patient-005`: abnormal A1c suppressed by follow-up evidence.

Do not add real patient names, addresses, phone numbers, emails, identifiers, access tokens, or refresh tokens to this repository.

All generated summaries are framed as clinician support. The app does not diagnose, prescribe, or replace clinical judgement. Reusable safety validation flags disallowed recommendation phrases before clinician-facing payloads are returned.

## Hackathon Scoring Notes

### AI Factor

Follow-Up Radar combines Prompt Opinion MCP orchestration with an internal,
guardrailed narrative layer. The deterministic services decide what was found, what
was suppressed, and which priority tier applies. The optional LLM only summarizes
that structured evidence for clinician review, and fallback mode keeps the demo
working without an API key.

### Potential Impact

The product targets a common primary-care operations gap: abnormal results that may
need documented follow-up. The workflow is designed to surface a review queue,
show audit evidence, and support clinician confirmation before any downstream task
or note is created.

### Feasibility

The current build is intentionally narrow and deployable: synthetic FHIR fixtures,
FastMCP tools, Render Docker deployment, health checks, smoke tests, rule profiles,
audit trail, in-memory demo state, and a provider interface that can be disabled.

### HIPAA And Production Readiness

This repository is demo-only and must not receive PHI. A production version would
need a HIPAA-eligible hosting path and BAA, encrypted storage, tenant-aware access
controls, least-privilege SMART scopes, audit-log retention, monitoring, incident
response procedures, formal security review, and reviewed EHR write workflows.
