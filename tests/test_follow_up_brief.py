from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.safety.output_validation import find_disallowed_clinical_phrases
from app.services.brief_generator import generate_follow_up_brief
from app.services.note_drafter import draft_clinician_note


def test_follow_up_brief_includes_disclaimer() -> None:
    brief = generate_follow_up_brief()

    assert brief["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert brief["findings"]
    assert "clinician review" in brief["summary"].lower()
    assert find_disallowed_clinical_phrases(str(brief)) == []


def test_follow_up_brief_clean_patient_includes_disclaimer_without_findings() -> None:
    brief = generate_follow_up_brief(patient_id="synthetic-patient-004")

    assert brief["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert brief["findings"] == []
    assert (
        brief["summary"]
        == "No unresolved abnormal results were found in the synthetic fixture data."
    )


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
    assert CLINICIAN_REVIEW_DISCLAIMER.lower() in note
    assert all(phrase not in note for phrase in forbidden_phrases)
    assert find_disallowed_clinical_phrases(note) == []
