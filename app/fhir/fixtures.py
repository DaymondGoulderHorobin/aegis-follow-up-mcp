"""Synthetic FHIR fixture loading helpers."""

from __future__ import annotations

import json
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config import settings


@lru_cache(maxsize=4)
def load_synthetic_bundle(path: str | Path | None = None) -> dict[str, Any]:
    bundle_path = Path(path) if path is not None else settings.fixture_bundle_path
    with bundle_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def iter_resources(
    resource_type: str | None = None,
    bundle: dict[str, Any] | None = None,
) -> Iterable[dict[str, Any]]:
    source_bundle = bundle or load_synthetic_bundle()
    for entry in source_bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource_type is None or resource.get("resourceType") == resource_type:
            yield resource


def first_resource(resource_type: str, bundle: dict[str, Any] | None = None) -> dict[str, Any]:
    return next(iter_resources(resource_type, bundle), {})


def find_resource_by_id(
    resource_type: str,
    resource_id: str | None,
    bundle: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not resource_id:
        return None
    for resource in iter_resources(resource_type, bundle):
        if resource.get("id") == resource_id:
            return resource
    return None


def default_patient_id(bundle: dict[str, Any] | None = None) -> str | None:
    patient = first_resource("Patient", bundle)
    return patient.get("id") if patient else None
