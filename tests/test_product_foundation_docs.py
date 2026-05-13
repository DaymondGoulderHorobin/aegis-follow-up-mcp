from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "SECURITY.md",
    "PRIVACY.md",
    "CLINICAL_SAFETY.md",
    "PRODUCT_LIMITATIONS.md",
    "docs/environment_profiles.md",
    "docs/production_readiness_checklist.md",
    "docs/pilot_runbook.md",
    "docs/codex_development_guide.md",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_product_foundation_docs_exist() -> None:
    missing = [path for path in REQUIRED_DOCS if not (ROOT / path).is_file()]

    assert missing == []


def test_governance_docs_keep_clinical_safety_boundaries() -> None:
    combined = "\n".join(
        _read(path)
        for path in [
            "SECURITY.md",
            "PRIVACY.md",
            "CLINICAL_SAFETY.md",
            "PRODUCT_LIMITATIONS.md",
        ]
    ).lower()

    assert "clinical decision support only" in combined
    assert "clinician review" in combined
    assert "not a diagnosis or treatment directive" in combined
    assert "autonomous" in combined
    assert "ehr write" in combined
    assert "offline_access" in combined
    assert "refresh-token" in combined or "refresh token" in combined


def test_environment_profile_docs_preserve_safe_defaults() -> None:
    environment_docs = _read("docs/environment_profiles.md")
    env_example = _read(".env.example")

    assert "APP_ENV=local" in env_example
    assert "FIXTURE_MODE=true" in env_example
    assert "LIVE_FHIR_READS_ENABLED=false" in env_example
    assert "LLM_PROVIDER=disabled" in env_example
    assert "GEMINI_API_KEY=\n" in env_example
    assert "local" in environment_docs
    assert "demo" in environment_docs
    assert "staging" in environment_docs
    assert "pilot" in environment_docs
    assert "production" in environment_docs


def test_docs_do_not_contain_real_secret_shapes() -> None:
    combined = "\n".join(
        _read(path)
        for path in [
            ".env.example",
            "SECURITY.md",
            "PRIVACY.md",
            "docs/environment_profiles.md",
            "docs/pilot_runbook.md",
        ]
    )

    assert "AIza" not in combined
    assert "Bearer " not in combined
    assert "GEMINI_API_KEY=AIza" not in combined
