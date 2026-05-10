from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.services.ai_follow_up_brief import generate_ai_follow_up_brief
from app.services.llm_provider import (
    DisabledLLMClient,
    LLMConfig,
    LLMResponse,
    create_llm_client,
)


class StaticLLMClient:
    provider_name = "fake"
    model = "fake-model"

    def __init__(self, text: str):
        self.text = text

    def generate(self, system_instruction: str, user_prompt: str) -> LLMResponse:
        return LLMResponse(provider=self.provider_name, model=self.model, text=self.text)


def test_ai_brief_uses_fallback_when_llm_provider_disabled() -> None:
    result = generate_ai_follow_up_brief(
        patient_id="synthetic-patient-001",
        llm_client=DisabledLLMClient(),
    )

    assert result["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert result["fallback_used"] is True
    assert result["fallback_reason"] == "llm_disabled"
    assert result["structured_findings"][0]["display"] == "Hemoglobin A1c"
    assert result["safety_validation"]["passed"] is True


def test_ai_brief_uses_fallback_when_gemini_key_missing() -> None:
    missing_key_client = create_llm_client(
        LLMConfig(provider="gemini", api_key="", model="gemini-2.5-flash")
    )

    result = generate_ai_follow_up_brief(
        patient_id="synthetic-patient-001",
        llm_client=missing_key_client,
    )

    assert result["llm_provider"] == "gemini"
    assert result["llm_model"] == "gemini-2.5-flash"
    assert result["fallback_used"] is True
    assert result["fallback_reason"] == "missing_api_key"


def test_ai_brief_accepts_safe_fake_llm_text() -> None:
    result = generate_ai_follow_up_brief(
        patient_id="synthetic-patient-001",
        llm_client=StaticLLMClient(
            "Clinician may wish to review the unresolved A1c and LDL findings and "
            "confirm whether follow-up is documented."
        ),
    )

    assert result["source"] == "llm_generated_with_deterministic_guardrails"
    assert result["fallback_used"] is False
    assert result["safety_validation"] == {"passed": True, "blocked_phrases": []}
    assert result["narrative"].startswith(CLINICIAN_REVIEW_DISCLAIMER)


def test_ai_brief_blocks_unsafe_fake_llm_text_and_returns_fallback() -> None:
    result = generate_ai_follow_up_brief(
        patient_id="synthetic-patient-001",
        llm_client=StaticLLMClient("The patient should start lipid-lowering therapy."),
    )

    assert result["fallback_used"] is True
    assert result["fallback_reason"] == "safety_validation_failed"
    assert result["safety_validation"]["passed"] is False
    assert "lipid-lowering therapy" in result["safety_validation"]["blocked_phrases"]
    assert "The patient should start" not in result["narrative"]


def test_ai_brief_cannot_change_deterministic_priority_or_findings() -> None:
    result = generate_ai_follow_up_brief(
        patient_id="synthetic-patient-003",
        llm_client=StaticLLMClient(
            "Clinician may wish to review later; priority tier is routine."
        ),
    )

    assert result["fallback_used"] is False
    assert result["priority"]["priority_tier"] == "same_day_clinician_review_consideration"
    assert [finding["display"] for finding in result["structured_findings"]] == ["Potassium"]
