# Environment Profiles

Aegis Follow-Up separates demo safety from future pilot and production work using
explicit environment profiles. These profiles are documentation guardrails today;
they should guide future code and deployment changes.

## Summary

| Profile | Purpose | Data posture | Expected defaults |
| --- | --- | --- | --- |
| `local` | Developer machine testing | Synthetic fixtures | `FIXTURE_MODE=true`, `LIVE_FHIR_READS_ENABLED=false`, `LLM_PROVIDER=disabled` |
| `demo` | Prompt Opinion marketplace demo | Synthetic fixtures | Public demo endpoint, no PHI, no live FHIR dependency |
| `staging` | Internal pre-pilot validation | Sandbox or approved test data | Managed secrets, read-only FHIR only, no broad scopes |
| `pilot` | Customer-approved clinical pilot | Customer-governed PHI | Authentication required, tenant-aware config, PHI-safe logs |
| `production` | Future commercial deployment | Customer-governed PHI | Out of scope for Sprint 1; use readiness checklist |

## Core Environment Variables

| Variable | Safe demo value | Notes |
| --- | --- | --- |
| `APP_ENV` | `local` or `demo` | Names the operating profile. |
| `FIXTURE_MODE` | `true` | Keeps synthetic fixtures as the primary data source. |
| `LIVE_FHIR_READS_ENABLED` | `false` | Enables only the optional FHIR proof when deliberately set true. |
| `FHIR_SYNTHETIC_BUNDLE_PATH` | `data/synthetic_patient_bundle.json` | Synthetic fixture path. |
| `LLM_PROVIDER` | `disabled` | Set to `gemini` only for controlled real LLM validation. |
| `GEMINI_API_KEY` | blank | Use managed secrets only; never commit a value. |
| `LLM_MODEL` | `gemini-2.5-flash` | Configured model name for Gemini mode. |
| `MCP_TRANSPORT` | `streamable-http` | Prompt Opinion-compatible transport. |
| `ALLOWED_ORIGINS` | blank for demo | Configure only for controlled browser clients. |

## Local

Use for development and tests.

```text
APP_ENV=local
FIXTURE_MODE=true
LIVE_FHIR_READS_ENABLED=false
LLM_PROVIDER=disabled
```

Local mode should run with no external secrets and no network dependency for the
core test suite.

## Demo

Use for Prompt Opinion marketplace demonstration.

```text
APP_ENV=demo
FIXTURE_MODE=true
LIVE_FHIR_READS_ENABLED=false
LLM_PROVIDER=disabled
```

Gemini may be enabled in Render for a controlled final demo, but fallback mode
must remain reliable.

## Staging

Use for internal pre-pilot validation with managed secrets.

```text
APP_ENV=staging
FIXTURE_MODE=true
LIVE_FHIR_READS_ENABLED=false
```

For optional FHIR reachability testing, temporarily set
`LIVE_FHIR_READS_ENABLED=true` and use sandbox FHIR credentials only. Turn it off
after the proof.

## Pilot

Use only after customer approval, authentication, privacy review, and clinical
safety review.

Pilot posture should include:

- authentication;
- tenant-aware configuration;
- read-only FHIR access first;
- PHI-safe logs;
- clinician review for every finding;
- no autonomous EHR writes.

## Future Production

Production is out of scope for Sprint 1. Use
`docs/production_readiness_checklist.md` before claiming production readiness.
