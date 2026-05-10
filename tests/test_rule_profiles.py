import pytest

from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.services.rule_profiles import (
    DEFAULT_PROFILE_ID,
    get_rule_profile,
    list_rule_profiles,
    priority_override_for_display,
)


def test_rule_profiles_load_static_profiles() -> None:
    payload = list_rule_profiles()
    profile_ids = {profile["profile_id"] for profile in payload["profiles"]}

    assert payload["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert payload["default_profile_id"] == DEFAULT_PROFILE_ID
    assert {
        "default_primary_care",
        "metabolic_follow_up",
        "cardiovascular_follow_up",
        "safety_critical_labs",
    }.issubset(profile_ids)


def test_rule_profile_priority_override() -> None:
    assert (
        priority_override_for_display("Potassium")
        == "same_day_clinician_review_consideration"
    )
    assert (
        priority_override_for_display("LDL cholesterol", "cardiovascular_follow_up")
        == "soon_clinician_review_consideration"
    )


def test_unknown_rule_profile_is_rejected_clearly() -> None:
    with pytest.raises(ValueError, match="Unknown rule profile"):
        get_rule_profile("not-a-profile")
