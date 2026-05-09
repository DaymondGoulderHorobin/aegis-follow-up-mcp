"""Small FHIR client scaffold for future external FHIR server mode."""

from __future__ import annotations

from typing import Any

import httpx

from app.fhir.context import FHIRContext
from app.fhir.fixtures import load_synthetic_bundle


class FHIRClient:
    """Fetch FHIR resources from either fixtures or an external server."""

    def __init__(self, context: FHIRContext):
        self.context = context

    async def patient_everything(self) -> dict[str, Any]:
        if self.context.fixture_mode:
            return load_synthetic_bundle()

        if not self.context.server_url or not self.context.access_token:
            return load_synthetic_bundle()

        headers = {"Authorization": f"Bearer {self.context.access_token}"}
        patient_id = self.context.patient_id or ""
        async with httpx.AsyncClient(base_url=self.context.server_url, timeout=20.0) as client:
            response = await client.get(f"/Patient/{patient_id}/$everything", headers=headers)
            response.raise_for_status()
            return response.json()
