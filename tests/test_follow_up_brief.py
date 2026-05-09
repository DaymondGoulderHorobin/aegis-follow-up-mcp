from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.services.brief_generator import generate_follow_up_brief
from app.services.note_drafter import draft_clinician_note


def test_follow_up_brief_includes_disclaimer() -> None:
    brief = generate_follow_up_brief()

    assert brief["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert brief["findings"]
    assert "clinician review" in brief["summary"].lower()


def test_draft_note_avoids_diagnostic_or_directive_phrasing() -> None:
    note = draft_clinician_note().lower()

    forbidden_phrases = [
        "diagnosed with",
        "start treatment",
        "prescribe",
        "must treat",
        "should start",
    ]
    assert "for clinician review" in note
    assert all(phrase not in note for phrase in forbidden_phrases)
