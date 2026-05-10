from app.safety.disclaimers import CLINICIAN_REVIEW_DISCLAIMER
from app.services.audit_trail import explain_result_decisions


def test_audit_trail_flags_unresolved_a1c_and_ldl() -> None:
    audit = explain_result_decisions(patient_id="synthetic-patient-001")
    flagged = {
        decision["display"]: decision
        for decision in audit["decisions"]
        if decision["decision"] == "flagged"
    }

    assert audit["disclaimer"] == CLINICIAN_REVIEW_DISCLAIMER
    assert audit["decision_counts"]["flagged"] == 2
    assert set(flagged) == {"Hemoglobin A1c", "LDL cholesterol"}
    assert flagged["Hemoglobin A1c"]["rule_id"] == "abnormal-no-follow-up-v1"


def test_audit_trail_includes_suppressed_potassium_evidence() -> None:
    audit = explain_result_decisions(patient_id="synthetic-patient-001")
    suppressed = [
        decision
        for decision in audit["decisions"]
        if decision["decision"] == "suppressed"
    ]

    assert len(suppressed) == 1
    assert suppressed[0]["display"] == "Potassium"
    assert suppressed[0]["suppression_reason"]
    assert "ServiceRequest/service-repeat-potassium" in suppressed[0]["suppression_reason"]


def test_audit_trail_flags_critical_synthetic_patient() -> None:
    audit = explain_result_decisions(patient_id="synthetic-patient-003")

    assert audit["decision_counts"] == {"flagged": 1, "suppressed": 0}
    assert audit["decisions"][0]["display"] == "Potassium"
    assert audit["decisions"][0]["severity"] == "high"
