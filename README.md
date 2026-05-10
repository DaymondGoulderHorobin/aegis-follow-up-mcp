# Follow-Up Radar MCP

Follow-Up Radar is a clinician-facing MCP server that reviews synthetic FHIR patient data for potentially unresolved abnormal results and generates a structured follow-up brief for clinician review.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Hackathon Positioning

- Project: Agents Assemble Prompt Opinion Hackathon
- Protocol: MCP server first
- Data mode: synthetic FHIR fixtures only
- Target MCP endpoint: `/mcp/`
- Health endpoints: `/healthz`, `/readyz`, `/version`
- Current version: `0.5.0`

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
- `draft_clinician_note`
- `assess_follow_up_priority`

The code registers these tools with FastMCP when the `fastmcp` package is installed. In local fixture-only test environments without FastMCP, `/mcp` returns tool metadata so the rest of the project remains testable.

`assess_follow_up_priority` returns deterministic clinician-review priority tiers:

- `same_day_clinician_review_consideration`
- `soon_clinician_review_consideration`
- `routine_clinician_review`
- `no_unresolved_abnormal_result_found`

It does not return diagnosis, prescribing, treatment-plan, or medication-adjustment instructions.

For MCP Inspector and deployment guidance, see:

- `docs/mcp_inspector.md`
- `docs/deployment.md`
- `docs/prompt_opinion_setup.md`

## Prompt Opinion Integration Notes

The server stays MCP-first and deterministic. Sprint 4 advertises Prompt Opinion's FHIR-context MCP extension during initialize:

```text
capabilities.extensions.ai.promptopinion/fhir-context
```

Requested SMART scopes are optional by default:

- `patient/Patient.rs`
- `patient/Observation.rs`
- `patient/Condition.rs`
- `patient/MedicationStatement.rs`
- `patient/Encounter.rs`

The server does not request `offline_access`, does not handle refresh tokens, does not fetch real FHIR data, and does not add an LLM layer.

If a Prompt Opinion user trusts the server and authorizes FHIR context, these headers may be sent to tool calls:

- `X-FHIR-Server-URL`
- `X-FHIR-Access-Token`
- `X-Patient-ID`

If any required context is missing, the app uses fixture mode.

## Synthetic Data And Safety

The included fixture data is synthetic and intentionally small for a reliable hackathon demo. Sprint 5 includes multiple synthetic outcomes:

- `synthetic-patient-001`: unresolved A1c and LDL, with potassium suppressed by follow-up evidence.
- `synthetic-patient-003`: high potassium without follow-up evidence for priority triage testing.
- `synthetic-patient-004`: clean chart with no unresolved abnormal results.
- `synthetic-patient-005`: abnormal A1c suppressed by follow-up evidence.

Do not add real patient names, addresses, phone numbers, emails, identifiers, access tokens, or refresh tokens to this repository.

All generated summaries are framed as clinician support. The app does not diagnose, prescribe, or replace clinical judgement. Reusable safety validation flags disallowed recommendation phrases before clinician-facing payloads are returned.
