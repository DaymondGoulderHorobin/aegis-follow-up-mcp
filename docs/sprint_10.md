# Sprint 10

## Objective

Add a narrow FHIR connectivity proof while keeping Aegis Follow-Up's primary demo
deterministic, synthetic, and clinician-review focused.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Branch

```text
codex/sprint-10-fhir-connectivity
```

## Scope

- Add `validate_fhir_context_connection` as an optional MCP tool.
- Use `X-FHIR-Server-URL`, `X-FHIR-Access-Token`, and `X-Patient-ID` only from
  runtime FHIR context headers.
- Attempt `GET /Patient/{patient_id}` only when context is complete and
  `LIVE_FHIR_READS_ENABLED=true`.
- Return safe metadata only: status, HTTP status, resource type, and boolean
  safety fields.
- Keep abnormal-result, task, audit, handoff, and AI workflows synthetic by default.
- Update judge guidance so the primary 5-tool happy path is unmistakable.

## Safety Boundary

- No access tokens are returned, logged, stored, or committed.
- No PHI-heavy FHIR payload is returned.
- No `offline_access` or refresh-token support is added.
- No live FHIR result influences clinical logic.
- No EHR writes are performed.

## Validation

```bash
python -m pytest
ruff check .
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/ --attempts 2 --delay-seconds 1 --timeout 30
```

Optional live FHIR proof:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --expect-live-fhir --fhir-server-url https://example.fhir.test --fhir-access-token <token> --fhir-patient-id <patient-id>
```
