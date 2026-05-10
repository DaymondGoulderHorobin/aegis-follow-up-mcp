# MCP Inspector

Follow-Up Radar uses FastMCP `streamable-http` transport at `/mcp`. A plain browser `GET /mcp` can return `406` because MCP clients must send protocol-specific headers and JSON-RPC payloads. Use MCP Inspector or the smoke script instead.

## Local Server

```bash
python -m pip install -e ".[dev]"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health checks:

```bash
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz
curl http://127.0.0.1:8000/version
```

Expected MCP endpoint:

```text
http://127.0.0.1:8000/mcp/
```

## MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

In Inspector:

1. Select streamable HTTP transport.
2. Set the URL to `http://127.0.0.1:8000/mcp/`.
3. Connect and initialize.
4. Confirm these tools are listed:
   - `get_patient_snapshot`
   - `get_recent_observations`
   - `find_unresolved_abnormal_results`
   - `generate_follow_up_brief`
   - `draft_clinician_note`
5. Call `find_unresolved_abnormal_results` with:
   ```json
   {"patient_id": "synthetic-patient-001"}
   ```
6. Call `generate_follow_up_brief` with the same patient ID.

Expected result: the first patient has unresolved A1c and LDL findings, while potassium is suppressed because the synthetic bundle includes follow-up evidence.

## Initialize Capabilities

Sprint 4 advertises Prompt Opinion FHIR-context support during initialize:

```text
capabilities.extensions.ai.promptopinion/fhir-context
```

Expected scopes:

- `patient/Patient.rs`
- `patient/Observation.rs`
- `patient/Condition.rs`
- `patient/MedicationStatement.rs`
- `patient/Encounter.rs`

All scopes should be optional. `offline_access` should not appear.

If MCP Inspector does not expose the raw initialize response, use the scripted smoke check below. The smoke script validates the extension payload before listing tools.

## Header Context Check

When the client supports custom HTTP headers, send:

```text
X-Patient-ID: synthetic-patient-002
X-FHIR-Server-URL: https://example.fhir.test
X-FHIR-Access-Token: synthetic-token-for-local-testing
```

Then call `get_patient_snapshot` without a `patient_id` argument. The tool should select `synthetic-patient-002`. Token values are parsed in memory only and are not logged or returned.

## Scripted Smoke Check

With the server running:

```bash
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/
```

The script initializes the MCP client, validates the Prompt Opinion FHIR-context extension payload, lists tools, and calls two tools against synthetic fixture mode.
