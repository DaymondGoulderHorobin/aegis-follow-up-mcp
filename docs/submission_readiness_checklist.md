# Submission Readiness Checklist

Use this checklist for final marketplace submission and demo recording.

## Repository And Deployment

- [ ] GitHub repository URL confirmed:
  `https://github.com/DaymondGoulderHorobin/aegis-follow-up-mcp`
- [ ] Render base endpoint confirmed:
  `https://aegis-follow-up-mcp.onrender.com`
- [ ] MCP endpoint confirmed:
  `https://aegis-follow-up-mcp.onrender.com/mcp/`
- [ ] `/healthz` returns healthy status.
- [ ] `/readyz` returns ready status.
- [ ] `/version` returns project `Aegis Follow-Up` and version `0.10.0`.

## Fallback Validation

- [ ] Fallback smoke passes:
  ```bash
  python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --attempts 3 --delay-seconds 2 --timeout 30
  ```
- [ ] Prompt Opinion discovers the final 15 tools.
- [ ] Prompt Opinion shows the FHIR-context extension or trust flow.
- [ ] Prompt Opinion FHIR-context scopes are optional.
- [ ] `offline_access` is not requested.
- [ ] Primary demo path runs without real PHI or live FHIR reads.

## Gemini Validation

- [ ] Gemini is configured only in Render environment variables.
- [ ] `LLM_PROVIDER=gemini` is set only when testing real Gemini mode.
- [ ] `LLM_MODEL=gemini-2.5-flash` is set.
- [ ] `GEMINI_API_KEY` is stored only as a Render secret.
- [ ] No Gemini key appears in GitHub, docs, logs, prompts, or screenshots.
- [ ] Gemini smoke passes after Render secrets are configured:
  ```bash
  python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --expect-real-llm
  ```
- [ ] `generate_ai_follow_up_brief` returns `fallback_used: false` in Gemini mode.
- [ ] `source` is `llm_generated_with_deterministic_guardrails` in Gemini mode.
- [ ] `safety_validation.passed: true`.

## Optional FHIR Connectivity Proof

- [ ] Primary demo keeps `LIVE_FHIR_READS_ENABLED=false`.
- [ ] Optional proof uses only a test FHIR server and temporary token.
- [ ] Optional proof is run only after `LIVE_FHIR_READS_ENABLED=true` is set.
- [ ] Supported smoke command is used:
  ```bash
  python scripts/smoke_mcp.py --url https://aegis-follow-up-mcp.onrender.com/mcp/ --expect-live-fhir --fhir-server-url https://example.fhir.test --fhir-access-token <token> --fhir-patient-id <patient-id>
  ```
- [ ] Note: the smoke script supports `--expect-live-fhir`; it does not expose a
  separate `--expect-fhir-connectivity` flag.
- [ ] The optional proof returns safe metadata only.
- [ ] No access token, patient demographics, or full FHIR payload appears in output.
- [ ] `LIVE_FHIR_READS_ENABLED=false` is restored after optional proof testing.

## Submission Assets

- [ ] `docs/marketplace_listing.md` is ready.
- [ ] `docs/demo_script.md` is rehearsed.
- [ ] `docs/judge_testing_guide.md` is aligned with the five-tool path.
- [ ] `docs/prompt_opinion_setup.md` is ready.
- [ ] `docs/render_gemini_checklist.md` is ready.
- [ ] Logo asset exists: `docs/assets/aegis-follow-up-logo.svg`.
- [ ] Final demo recording is prepared.
- [ ] Final demo recording does not show secrets, PHI, or real tokens.

## Claim Discipline

- [ ] Do not claim diagnosis, prescribing, treatment, or therapy recommendations.
- [ ] Do not claim live FHIR reads are the primary demo path.
- [ ] Do not claim real EHR writes occur.
- [ ] Do not claim another agent was contacted by the handoff payload.
- [ ] Do not claim production compliance, BAA coverage, or clinical validation.
- [ ] State clearly: clinical decision support only, for clinician review.

## Final PR And CI

- [ ] Final documentation PR passes CI.
- [ ] Docker build passes in GitHub Actions.
- [ ] No secrets are committed.
- [ ] PR summary states readiness for marketplace submission after final Render and
  Prompt Opinion validation.
