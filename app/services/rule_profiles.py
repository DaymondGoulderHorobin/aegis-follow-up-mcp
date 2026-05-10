"""Static deterministic rule profile loading."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from app.config import settings
from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import (
    assert_clinician_facing_payload_safe,
    assert_disclaimer_present,
)

DEFAULT_PROFILE_ID = "default_primary_care"
PROFILE_DIR = settings.project_root / "data" / "rule_profiles"

PRIORITY_ORDER = {
    "same_day_clinician_review_consideration": 0,
    "soon_clinician_review_consideration": 1,
    "routine_clinician_review": 2,
    "no_unresolved_abnormal_result_found": 3,
}


@lru_cache(maxsize=1)
def load_rule_profiles() -> dict[str, dict[str, Any]]:
    """Load static rule profiles from repository fixtures."""

    profiles: dict[str, dict[str, Any]] = {}
    for path in sorted(PROFILE_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            profile = json.load(handle)
        profile_id = str(profile.get("profile_id", "")).strip()
        if not profile_id:
            raise ValueError(f"Rule profile file {path.name} is missing profile_id.")
        _validate_profile(profile)
        profiles[profile_id] = profile
    if DEFAULT_PROFILE_ID not in profiles:
        raise ValueError(f"Default rule profile {DEFAULT_PROFILE_ID!r} is missing.")
    return profiles


def list_rule_profiles() -> dict[str, Any]:
    """Return available deterministic rule profiles."""

    profiles = load_rule_profiles()
    payload = {
        "disclaimer": CLINICIAN_REVIEW_DISCLAIMER,
        "default_profile_id": DEFAULT_PROFILE_ID,
        "profiles": list(profiles.values()),
    }
    assert_disclaimer_present(payload)
    assert_clinician_facing_payload_safe(payload)
    return payload


def get_rule_profile(profile_id: str | None = None) -> dict[str, Any]:
    """Return one static rule profile or raise a clear error for unknown IDs."""

    resolved_profile_id = profile_id or DEFAULT_PROFILE_ID
    profiles = load_rule_profiles()
    if resolved_profile_id not in profiles:
        available = ", ".join(sorted(profiles))
        raise ValueError(
            f"Unknown rule profile {resolved_profile_id!r}. Available profiles: {available}."
        )
    return profiles[resolved_profile_id]


def priority_override_for_display(
    display: str,
    profile_id: str | None = None,
) -> str | None:
    """Return a configured priority override for an observation display."""

    profile = get_rule_profile(profile_id)
    overrides = profile.get("priority_overrides", {})
    if not isinstance(overrides, dict):
        return None
    value = overrides.get(display)
    if value in PRIORITY_ORDER:
        return str(value)
    return None


def highest_priority(tiers: list[str]) -> str:
    """Return the highest-priority tier from a list."""

    if not tiers:
        return "no_unresolved_abnormal_result_found"
    return min(tiers, key=lambda tier: PRIORITY_ORDER.get(tier, 999))


def _validate_profile(profile: dict[str, Any]) -> None:
    required = {"profile_id", "display_name", "description", "priority_overrides"}
    missing = sorted(required - set(profile))
    if missing:
        profile_id = profile.get("profile_id", "<unknown>")
        raise ValueError(f"Rule profile {profile_id} missing {missing}.")
    overrides = profile.get("priority_overrides")
    if not isinstance(overrides, dict):
        raise ValueError("priority_overrides must be an object.")
    invalid_tiers = sorted(
        {tier for tier in overrides.values() if tier not in PRIORITY_ORDER}
    )
    if invalid_tiers:
        raise ValueError(f"Rule profile has invalid priority tier(s): {invalid_tiers}.")
