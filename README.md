# Follow-Up Radar MCP

Follow-Up Radar is a clinician-facing MCP server that reviews synthetic FHIR patient data for potentially unresolved abnormal results and generates a structured follow-up brief for clinician review.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Hackathon Positioning

- Project: Agents Assemble Prompt Opinion Hackathon
- Protocol: MCP server first
- Sprint 1 data mode: synthetic FHIR fixtures only
- Target MCP endpoint: `/mcp`
- Health endpoints: `/healthz`, `/readyz`, `/version`

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

## MCP Tool Notes

Sprint 2 exposes these MCP tools:

- `get_patient_snapshot`
- `get_recent_observations`
- `find_unresolved_abnormal_results`
- `generate_follow_up_brief`
- `draft_clinician_note`

The code registers these tools with FastMCP when the `fastmcp` package is installed. In local fixture-only test environments without FastMCP, `/mcp` returns tool metadata so the rest of the project remains testable.

For MCP Inspector and deployment guidance, see:

- `docs/mcp_inspector.md`
- `docs/deployment.md`
- `docs/prompt_opinion_setup.md`

## Prompt Opinion Integration Notes

Sprint 1 keeps the server MCP-first and deterministic. Sprint 2 should verify Prompt Opinion MCP transport compatibility, run MCP Inspector, deploy the server to a public HTTPS endpoint, and connect that endpoint inside Prompt Opinion.

Expected FHIR context headers for future external mode:

- `X-FHIR-Server-URL`
- `X-FHIR-Access-Token`
- `X-Patient-ID`

If any required context is missing, the app uses fixture mode.

## Synthetic Data And Safety

The included fixture data is synthetic and intentionally small for a reliable hackathon demo. Do not add real patient names, addresses, phone numbers, emails, identifiers, access tokens, or refresh tokens to this repository.

All generated summaries are framed as clinician support. The app does not diagnose, prescribe, or replace clinical judgement.
