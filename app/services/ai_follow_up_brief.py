"""Controlled AI-assisted follow-up brief generation."""

from __future__ import annotations

import json
from typing import Any

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
    find_disallowed_clinical_phrases,
)
from app.services.abnormal_results import find_unresolved_abnormal_results
from app.services.audit_trail import explain_result_decisions
from app.services.follow_up_priority import assess_follow_up_priority
from app.services.follow_up_tasks import list_follow_up_tasks
from app.services.llm_provider import (
    LLMClient,
    LLMProviderError,
    create_llm_client,
)
from app.services.patient_snapshot import get_patient_snapshot
from app.services.rule_profiles import DEFAULT_PROFILE_ID

AI_BRIEF_SOURCE = "llm_generated_with_deterministic_guardrails"
FALLBACK_SOURCE = "deterministic_fallback_with_guardrails"

AI_NARRATIVE_SYSTEM_INSTRUCTION = """
You are generating a concise clinician-review narrative from deterministic structured data.
Do not diagnose.
Do not prescribe.
Do not recommend medication adjustment, therapy, or treatment.
Do not add clinical facts that are not present in the provided structured data.
Do not infer urgency beyond the supplied priority_tier.
Use neutral wording such as "clinician may wish to review" and
"confirm whether follow-up is documented".
Always state that the output is clinical decision support only and for clinician review.
Keep the response concise and audit-friendly.
""".strip()


def generate_ai_follow_up_brief(
    patient_id: str | None = None,
    profile_id: str = DEFAULT_PROFILE_ID,
    llm_client: LLMClient | None = None,
) -> dict[str, Any]:
    """Generate an optional LLM narrative around deterministic source evidence."""

    source_context = _build_source_context(patient_id=patient_id, profile_id=profile_id)
    client = llm_client or create_llm_client()
    provider_name = getattr(client, "provider_name", "unknown")
    model = getattr(client, "model", "unknown")
    fallback_reason: str | None = None
    safety_validation = {"passed": True, "blocked_phrases": []}

    try:
        llm_response = client.generate(
            system_instruction=AI_NARRATIVE_SYSTEM_INSTRUCTION,
            user_prompt=_build_user_prompt(source_context),
        )
        provider_name = llm_response.provider
        model = llm_response.model
        narrative = _with_disclaimer(llm_response.text)
        safety_validation = _validate_ai_narrative(narrative)
        if not safety_validation["passed"]:
            fallback_reason = "safety_validation_failed"
            narrative = _fallback_narrative(source_context)
    except LLMProviderError as exc:
        fallback_reason = exc.reason
        narrative = _fallback_narrative(source_context)
    except Exception:  # noqa: BLE001 - this is an optional provider safety boundary.
        fallback_reason = "api_error"
        narrative = _fallback_narrative(source_context)

    fallback_used = fallback_reason is not None
    if fallback_used and fallback_reason != "safety_validation_failed":
        safety_validation = _validate_ai_narrative(narrative)

    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "patient_id": source_context["patient"]["patient_id"],
        "profile_id": profile_id,
        "source": FALLBACK_SOURCE if fallback_used else AI_BRIEF_SOURCE,
        "llm_provider": provider_name,
        "llm_model": model,
        "narrative": narrative,
        "structured_findings": source_context["structured_findings"],
        "priority": source_context["priority"],
        "audit_summary": source_context["audit_summary"],
        "task_context": source_context["task_context"],
        "safety_validation": safety_validation,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload


def _build_source_context(patient_id: str | None, profile_id: str) -> dict[str, Any]:
    patient = get_patient_snapshot(patient_id=patient_id)
    findings = find_unresolved_abnormal_results(patient_id=patient.patient_id)
    priority = assess_follow_up_priority(
        patient_id=patient.patient_id,
        profile_id=profile_id,
    )
    audit = explain_result_decisions(
        patient_id=patient.patient_id,
        profile_id=profile_id,
    )
    task_queue = list_follow_up_tasks(
        profile_id=profile_id,
        patient_ids=[patient.patient_id],
    )
    return {
        "patient": {
            "patient_id": patient.patient_id,
            "name": patient.name,
            "birth_date": patient.birth_date,
            "sex": patient.sex,
        },
        "structured_findings": [finding.model_dump() for finding in findings],
        "priority": {
            "priority_tier": priority["priority_tier"],
            "summary": priority["summary"],
            "rationale": priority["rationale"],
        },
        "audit_summary": {
            "decision_counts": audit["decision_counts"],
            "flagged_decision_ids": [
                decision["decision_id"]
                for decision in audit["decisions"]
                if decision["decision"] == "flagged"
            ],
            "suppressed_decision_ids": [
                decision["decision_id"]
                for decision in audit["decisions"]
                if decision["decision"] == "suppressed"
            ],
        },
        "task_context": _flatten_task_groups(task_queue["task_groups"]),
    }


def _build_user_prompt(source_context: dict[str, Any]) -> str:
    prompt_payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "patient": source_context["patient"],
        "structured_findings": [
            {
                "display": finding["display"],
                "severity": finding["severity"],
                "reason": finding["reason"],
                "evidence": finding["evidence"],
            }
            for finding in source_context["structured_findings"]
        ],
        "priority": source_context["priority"],
        "audit_summary": source_context["audit_summary"],
        "task_context": source_context["task_context"],
        "required_output": "Return one concise clinician-review narrative only.",
    }
    return json.dumps(prompt_payload, indent=2, sort_keys=True)


def _with_disclaimer(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise LLMProviderError("malformed_response")
    if CLINICIAN_REVIEW_DISCLAIMER in cleaned:
        return cleaned
    return f"{CLINICIAN_REVIEW_DISCLAIMER} {cleaned}"


def _validate_ai_narrative(narrative: str) -> dict[str, Any]:
    blocked = find_disallowed_clinical_phrases(narrative)
    return {"passed": not blocked, "blocked_phrases": blocked}


def _fallback_narrative(source_context: dict[str, Any]) -> str:
    patient_id = source_context["patient"]["patient_id"]
    priority_tier = source_context["priority"]["priority_tier"]
    findings = source_context["structured_findings"]
    if findings:
        finding_names = ", ".join(finding["display"] for finding in findings)
        finding_text = f"Deterministic review found unresolved abnormal result(s): {finding_names}."
    else:
        finding_text = "Deterministic review found no unresolved abnormal results."
    return (
        f"{CLINICIAN_REVIEW_DISCLAIMER} Synthetic patient {patient_id}: "
        f"{finding_text} Priority tier is {priority_tier}. Clinician may wish to review "
        "the structured findings, confirm whether follow-up is documented, and record "
        "review status if appropriate."
    )


def _flatten_task_groups(task_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        task
        for group in task_groups
        for task in group["tasks"]
    ]
