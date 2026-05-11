# Sprint 4

## Objective

Advertise Prompt Opinion FHIR-context support during MCP initialize while keeping Aegis Follow-Up deterministic, synthetic-data based, and clinician-review focused.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

## Branch

```text
codex/sprint-4-fhir-context-extension
```

## Extension Design

Sprint 4 declares Prompt Opinion's MCP FHIR-context extension under initialize capabilities:

```json
{
  "capabilities": {
    "extensions": {
      "ai.promptopinion/fhir-context": {
        "scopes": [
          {"name": "patient/Patient.rs", "required": false},
          {"name": "patient/Observation.rs", "required": false},
          {"name": "patient/Condition.rs", "required": false},
          {"name": "patient/MedicationStatement.rs", "required": false},
          {"name": "patient/Encounter.rs", "required": false}
        ]
      }
    }
  }
}
```

The implementation lives in `app/prompt_opinion/fhir_context_extension.py`.

FastMCP 3.2.4 does not expose a public extension-registration hook for initialize capabilities. The app uses a small compatibility adapter around FastMCP's low-level capability builder and merges the Prompt Opinion extension with any existing extension metadata.

## Scope Strategy

All requested SMART scopes are optional by default:

| Scope | Required | Reason |
| --- | --- | --- |
| `patient/Patient.rs` | No | Demographics and patient identity context. |
| `patient/Observation.rs` | No | Lab and observation context for abnormal-result review. |
| `patient/Condition.rs` | No | Condition context for follow-up summaries. |
| `patient/MedicationStatement.rs` | No | Medication context for snapshot and future review support. |
| `patient/Encounter.rs` | No | Encounter context for follow-up evidence. |

`offline_access` is intentionally absent. Sprint 4 does not implement refresh tokens, background access, real FHIR reads, or LLM summarisation.

## Runtime Behavior

If Prompt Opinion users trust the MCP server and authorize FHIR context, Prompt Opinion may send:

```text
X-FHIR-Server-URL
X-FHIR-Access-Token
X-Patient-ID
```

The server already parses those headers case-insensitively. Access tokens are kept in memory and redacted from safe summaries.

Fixture mode remains the default path. If FHIR context is absent, incomplete, or not authorized, tools continue to use the synthetic fixture data.

## Validation

Run locally:

```bash
python -m pytest
ruff check .
uvicorn app.main:app --host 127.0.0.1 --port 8000
python scripts/smoke_mcp.py --url http://127.0.0.1:8000/mcp/ --attempts 2 --delay-seconds 1 --timeout 20
```

The smoke script now verifies:

- MCP initialize succeeds.
- `capabilities.extensions` includes `ai.promptopinion/fhir-context`.
- The five approved scopes are present.
- No scope is required by default.
- `offline_access` is absent.
- All five tools are listed.
- The deterministic A1c, LDL, and safety-disclaimer checks still pass.

## Prompt Opinion Validation

1. Add the deployed `/mcp/` URL in Prompt Opinion.
2. Continue through initialization.
3. Confirm Prompt Opinion shows the FHIR-context trust or extension toggle.
4. Confirm all requested scopes are optional.
5. Leave the extension disabled to validate fixture-mode fallback.
6. Enable the extension and grant optional scopes only if testing Prompt Opinion header forwarding.
7. Invoke deterministic tools against `synthetic-patient-001`.

## Known Risks

- Prompt Opinion UI wording may differ from these docs while the integration is evolving.
- MCP Inspector may not display initialize extensions directly. Use the smoke script when the raw initialize response is not visible.
- Real external FHIR reads remain deferred until after marketplace invocation succeeds.

## Safety

- Synthetic data only.
- No PHI.
- No real FHIR credentials.
- No refresh token handling.
- No `offline_access` scope.
- No LLM summarisation.
- No diagnosis or treatment directives.
