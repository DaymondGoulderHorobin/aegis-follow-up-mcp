import pytest

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_clinician_facing_text_safe,
    assert_disclaimer_present,
    find_disallowed_clinical_phrases,
)


def test_safety_validator_flags_disallowed_recommendation_phrases() -> None:
    text = "The patient should start lipid-lowering therapy."

    assert find_disallowed_clinical_phrases(text) == [
        "should start",
        "lipid-lowering therapy",
    ]
    with pytest.raises(ValueError):
        assert_clinician_facing_text_safe(text)


def test_safety_validator_allows_neutral_review_language() -> None:
    text = (
        "Clinician may wish to review the result, confirm follow-up status, "
        "and document the plan if appropriate."
    )

    assert find_disallowed_clinical_phrases(text) == []
    assert_clinician_facing_text_safe(text)


def test_payload_validation_requires_disclaimer_and_checks_nested_text() -> None:
    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "summary": "No unresolved abnormal results were found.",
        "findings": [{"reason": "Clinician may wish to review the result."}],
    }

    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)


def test_payload_validation_rejects_missing_disclaimer() -> None:
    with pytest.raises(ValueError):
        assert_disclaimer_present({"summary": "Clinician review only."})
