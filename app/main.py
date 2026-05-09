"""HTTP entrypoint for health checks and MCP transport."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.mcp_server import get_mcp_asgi_app, get_registered_tool_names


def create_app() -> FastAPI:
    mcp_asgi_app = get_mcp_asgi_app()
    api = FastAPI(
        title=settings.project_name,
        version=settings.version,
        lifespan=getattr(mcp_asgi_app, "lifespan", None),
    )
    if settings.allowed_origins:
        api.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.allowed_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=[
                "authorization",
                "content-type",
                "mcp-session-id",
                "x-fhir-access-token",
                "x-fhir-server-url",
                "x-patient-id",
            ],
        )

    @api.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @api.get("/readyz")
    def readyz() -> dict[str, bool]:
        return {"ready": True}

    @api.get("/version")
    def version() -> dict[str, str | bool]:
        return {
            "project": settings.project_name,
            "version": settings.version,
            "fixture_mode_default": settings.fixture_mode,
            "mcp_transport": settings.mcp_transport,
        }

    if mcp_asgi_app is not None:
        api.mount("/mcp", mcp_asgi_app)
    else:

        @api.get("/mcp")
        def mcp_metadata() -> dict[str, object]:
            return {
                "project": settings.project_name,
                "transport": "fastmcp-unavailable-local-metadata",
                "tools": get_registered_tool_names(),
            }

    return api


app = create_app()
