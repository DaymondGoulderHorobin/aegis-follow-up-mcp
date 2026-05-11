# Risk Register

This register tracks known risks for Aegis Follow-Up as a hackathon submission and
future commercial Prompt Opinion MCP product.

Clinical decision support only. For clinician review. Not a diagnosis or treatment directive.

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Hallucinated AI language | AI narrative could overstate urgency, diagnosis, or action. | Keep deterministic evidence as source of truth, use safety validation, preserve fallback mode, and instruct Prompt Opinion not to embellish. |
| Overclaiming clinical capability | Judges or buyers may misunderstand the product as diagnostic or autonomous. | Use consistent disclaimers, five-tool demo framing, and explicit "no diagnosis, prescribing, treatment, or autonomous write" language. |
| Live FHIR data quality issues | Missing or inconsistent records could cause incorrect follow-up interpretation. | Start with read-only pilots, add data quality diagnostics, preserve audit trails, and require clinician review. |
| Missing follow-up evidence | A real follow-up action may not be represented in available FHIR resources. | Expand evidence mapping, display suppressed/flagged rationale, support dismissal reasons, and avoid autonomous escalation. |
| False positives | The queue may include items that were already addressed. | Provide audit explanations, suppression evidence, reviewer dismissal workflows, and tenant-specific rules. |
| False negatives | The system may miss unresolved abnormal results. | Expand fixture coverage, review rules with clinicians, monitor missed cases in pilots, and avoid claims of completeness. |
| Token handling | FHIR access tokens could be exposed in logs, outputs, or recordings. | Keep tokens runtime-only, return token presence as booleans, redact sensitive headers, avoid screenshots with tokens, and use Render secrets for operational keys. |
| PHI exposure | Real patient data could appear in logs, docs, tests, or demos. | Keep hackathon demo synthetic, do not commit PHI, avoid logging payloads, and return metadata only from the connectivity proof. |
| EHR writeback risk | Writes could create incorrect tasks, notes, or care coordination requests. | Defer writeback, require clinician approval, add dry-run mode, use minimal scopes, and maintain full audit logs. |
| Workflow burden | Extra queue items may increase clinician workload. | Prioritize high-signal cases, support dismissal reasons, tune thresholds, and measure queue volume and review time. |
| Regulatory positioning | Product claims could drift toward regulated diagnosis or treatment recommendations. | Maintain clinical decision support framing, get legal/regulatory review before commercialization, and avoid autonomous treatment directives. |
| Prompt/client behavior variance | Different MCP clients may present tool output or FHIR trust flows differently. | Validate in Prompt Opinion, keep outputs self-describing, and provide judge/setup guidance. |
| Gemini configuration errors | Missing or exposed API keys could break demo or leak secrets. | Keep fallback mode reliable, configure Gemini only in Render secrets, and run real LLM smoke only after fallback passes. |
| Optional FHIR proof fragility | External FHIR server downtime could distract from the main demo. | Keep proof optional, use fallback smoke as primary validation, and label live FHIR as reachability only. |
