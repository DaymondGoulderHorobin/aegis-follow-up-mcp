# Aegis Follow-Up

![Aegis Follow-Up logo](docs/assets/aegis-follow-up-logo.svg)

Aegis Follow-Up is a clinician-review MCP safety layer that turns patient-context
data into auditable follow-up tasks, controlled AI summaries, and handoff-ready
payloads.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

The GitHub repository and Render service are now `aegis-follow-up-mcp`. The Python
package name remains `follow-up-radar-mcp` for import and installation stability.

## Hackathon Positioning

- Project: Agents Assemble Prompt Opinion Hackathon
- Marketplace brand: `Aegis Follow-Up`
- Stable deployed MCP endpoint: `https://aegis-follow-up-mcp.onrender.com/mcp/`
- Transport: Streamable HTTP
- Authentication: none for the synthetic-data hackathon demo
- Data mode: synthetic FHIR fixtures by default
- Current version: `0.9.0`

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

## Validate

```bash
pytest
ruff check .
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/
```

## MCP Tools

Aegis Follow-Up exposes 14 MCP tools:

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
- `get_fhir_connection_status`
- `create_follow_up_handoff_payload`
- `update_follow_up_task_status`
- `get_ehr_integration_summary`

The code registers these tools with FastMCP when `fastmcp` is installed. In local
fixture-only test environments without FastMCP, `/mcp` returns tool metadata so the
project remains testable.

## Two-AI-Layer Architecture

```text
Prompt Opinion agent
-> chooses which MCP tools to invoke
-> Aegis Follow-Up deterministic review
-> audit trail, priority queue, rule profiles, and handoff payloads
-> optional Gemini narrative synthesis
-> safety validator blocks unsafe wording or falls back
-> clinician review remains required
```

Prompt Opinion may use AI to interpret the user request and select MCP tools. Aegis
Follow-Up performs deterministic follow-up review and can optionally call Gemini for
concise narrative synthesis from structured deterministic source context. Gemini is
not the source of truth: deterministic findings, priority tier, audit trail, and
task context remain authoritative.

## FHIR Transparency

Aegis Follow-Up advertises Prompt Opinion's FHIR-context MCP extension during
initialize:

```text
capabilities.extensions.ai.promptopinion/fhir-context
```

Requested SMART scopes are optional by default:

- `patient/Patient.rs`
- `patient/Observation.rs`
- `patient/Condition.rs`
- `patient/MedicationStatement.rs`
- `patient/Encounter.rs`

The demo does not request `offline_access`, does not handle refresh tokens, and
does not perform live FHIR reads. `get_fhir_connection_status` reports whether FHIR
headers are present and whether the active source is `synthetic_fixture_data`.

## Safety

- Synthetic fixture data only for the hackathon demo.
- No PHI is committed, required, logged, or returned.
- No real EHR writes.
- No autonomous handoff dispatch.
- No diagnosis, prescribing, therapy, medication, or treatment recommendations.
- AI narrative output is optional, safety-validated, and backed by deterministic fallback.
- Handoff payloads return `payload_only: true`, `required_human_review: true`, and `ehr_write_performed: false`.

## Hackathon Scoring Notes

### AI Factor

Aegis Follow-Up demonstrates two AI layers with clear boundaries. Prompt Opinion
chooses tools, while the MCP server optionally uses Gemini only to summarize
deterministic evidence. Safety validation blocks unsafe output and falls back to a
deterministic narrative.

### Potential Impact

The product targets a common primary-care operations gap: abnormal results that may
need documented follow-up. It surfaces a priority queue, explains why each result
was flagged or suppressed, and creates handoff-ready payloads for future scheduling
or care-coordination workflows.

### Feasibility

The demo is already deployable on Render with health checks, smoke tests, Prompt
Opinion FHIR-context support, deterministic fallback mode, and no required secrets.
Production work would add HIPAA-eligible hosting, BAA coverage, persistent audit
storage, access controls, monitoring, and reviewed EHR write workflows.

## Final Submission Docs

- `docs/marketplace_listing.md`
- `docs/demo_script.md`
- `docs/judge_testing_guide.md`
- `docs/render_gemini_checklist.md`
- `docs/prompt_opinion_setup.md`
- `docs/prompt_opinion_agent_instructions.md`
- `docs/submission_copy.md`
