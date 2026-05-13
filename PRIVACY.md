# Privacy Policy

## Current Demo Data

Aegis Follow-Up uses synthetic FHIR fixture data by default. The public demo does
not require PHI, real patient data, real FHIR credentials, or live EHR access.

Synthetic fixture patients are used to demonstrate follow-up logic, audit trails,
AI narrative guardrails, and handoff payload shape. They must not be treated as
clinical validation data.

## Live FHIR And PHI Boundaries

Live FHIR data is sensitive and customer-governed. Any use of real PHI requires a
customer-approved deployment posture, appropriate agreements, authentication,
access controls, logging restrictions, and clinical review.

The optional FHIR connectivity proof is read-only and returns safe metadata only.
It must not return access tokens, patient demographics, or full FHIR payloads.

## Data Minimization

Future pilots should collect the minimum data needed to support follow-up review:

- narrow read-only FHIR scopes;
- deterministic summary fields rather than raw payload storage where feasible;
- audit metadata without full PHI-bearing payloads in logs;
- explicit customer approval before retaining any clinical data.

## Logging And Retention Assumptions

The demo should log operational status only. It should not log PHI, raw FHIR
resources, Gemini prompts containing PHI, access tokens, or authorization
headers.

Until a customer-specific retention policy exists, assume no live PHI is retained
by this application. Synthetic fixtures can remain in the repository for testing.

## AI And Customer Data

The demo can use deterministic fallback mode without an LLM key. If Gemini is
enabled for a controlled demo or pilot, prompts must be built from reviewed,
structured evidence and must follow the customer's data-processing requirements.

Do not train on customer PHI unless a separate written agreement explicitly
approves that use.

## Pilot Privacy Checklist

- Confirm customer approval for any live FHIR or PHI access.
- Confirm authentication and tenant isolation.
- Confirm read-only FHIR scope boundaries.
- Confirm logging excludes PHI and tokens.
- Confirm Gemini or other LLM data-processing terms.
- Confirm incident response and deletion expectations.
- Confirm demo recordings and screenshots do not expose PHI.
