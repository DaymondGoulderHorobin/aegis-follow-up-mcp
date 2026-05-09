"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - exercised only in minimal environments
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_name: str = "Follow-Up Radar MCP"
    version: str = "0.1.0"
    app_env: str = os.getenv("APP_ENV", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    fixture_mode: bool = os.getenv("FIXTURE_MODE", "true").lower() == "true"

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def fixture_bundle_path(self) -> Path:
        configured_path = os.getenv(
            "FHIR_SYNTHETIC_BUNDLE_PATH",
            "data/synthetic_patient_bundle.json",
        )
        path = Path(configured_path)
        if not path.is_absolute():
            path = self.project_root / path
        return path


settings = Settings()
