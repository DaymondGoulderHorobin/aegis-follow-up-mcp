# Render And Gemini Final Checklist

Use this checklist after Sprint 10 is merged to `main`.

## Fallback Validation

1. Confirm Render redeployed from latest `main`.
2. Open:
   ```text
   https://aegis-follow-up-mcp.onrender.com/version
   ```
3. Confirm version `0.10.0`.
4. Run fallback smoke:
   ```bash
   python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --attempts 3 --delay-seconds 2 --timeout 30
   ```
5. Confirm Prompt Opinion tool discovery shows the final 15 tools.

## Optional FHIR Connectivity Proof

Leave `LIVE_FHIR_READS_ENABLED=false` for fallback validation. To prove FHIR
reachability with a non-production test server only, temporarily set:

```text
LIVE_FHIR_READS_ENABLED=true
```

Then supply Prompt Opinion/FastMCP headers for `X-FHIR-Server-URL`,
`X-FHIR-Access-Token`, and `X-Patient-ID`, and run:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --expect-live-fhir --fhir-server-url https://example.fhir.test --fhir-access-token <token> --fhir-patient-id <patient-id>
```

Turn `LIVE_FHIR_READS_ENABLED=false` again after the proof unless actively
testing FHIR connectivity. Do not commit or screenshot tokens.

## Gemini Configuration

Only configure Gemini after fallback smoke passes.

1. In Render service environment variables, set:
   ```text
   LLM_PROVIDER=gemini
   LLM_MODEL=gemini-2.5-flash
   ```
2. Add `GEMINI_API_KEY` as a Render secret value only.
3. Do not commit the key.
4. Do not include the key in screenshots, docs, logs, prompts, or recordings.
5. Redeploy the Render service.

## Real LLM Validation

Run:

```bash
python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --expect-real-llm
```

Then call `generate_ai_follow_up_brief` for `synthetic-patient-003` and confirm:

- `fallback_used: false`
- `source: llm_generated_with_deterministic_guardrails`
- `structured_findings` is still present
- `priority` is still present
- `audit_summary` is still present
- `safety_validation.passed: true`

## Demo Guardrails

- Keep `FIXTURE_MODE=true`.
- Keep `LIVE_FHIR_READS_ENABLED=false`.
- Do not configure real FHIR credentials.
- Do not claim a real EHR write occurred.
- Do not claim another agent was contacted by the handoff payload.
