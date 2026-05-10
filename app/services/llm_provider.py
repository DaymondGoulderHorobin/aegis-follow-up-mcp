"""Optional LLM provider interface for controlled narrative synthesis."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from app.config import settings


@dataclass(frozen=True)
class LLMConfig:
    provider: str = "disabled"
    api_key: str = ""
    model: str = "gemini-2.5-flash"
    timeout_seconds: float = 20
    max_output_tokens: int = 700


@dataclass(frozen=True)
class LLMResponse:
    provider: str
    model: str
    text: str


class LLMClient(Protocol):
    provider_name: str
    model: str

    def generate(self, system_instruction: str, user_prompt: str) -> LLMResponse:
        """Return narrative text or raise LLMProviderError."""


class LLMProviderError(RuntimeError):
    """Raised when an optional provider cannot return safe narrative text."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class DisabledLLMClient:
    provider_name = "disabled"
    model = "disabled"

    def generate(self, system_instruction: str, user_prompt: str) -> LLMResponse:
        raise LLMProviderError("llm_disabled")


class MissingKeyLLMClient:
    provider_name = "gemini"

    def __init__(self, model: str):
        self.model = model

    def generate(self, system_instruction: str, user_prompt: str) -> LLMResponse:
        raise LLMProviderError("missing_api_key")


class GeminiLLMClient:
    provider_name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_output_tokens: int,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens

    def generate(self, system_instruction: str, user_prompt: str) -> LLMResponse:
        payload = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": self.max_output_tokens,
            },
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.api_key,
                    },
                    json=payload,
                )
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise LLMProviderError("timeout") from exc
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            raise LLMProviderError("api_error") from exc

        try:
            response_payload = response.json()
        except ValueError as exc:
            raise LLMProviderError("malformed_response") from exc

        text = _text_from_gemini_response(response_payload)
        if not text:
            raise LLMProviderError("malformed_response")
        return LLMResponse(provider=self.provider_name, model=self.model, text=text)


def llm_config_from_env() -> LLMConfig:
    """Read LLM configuration dynamically so tests and deployments can override env."""

    return LLMConfig(
        provider=os.getenv("LLM_PROVIDER", settings.llm_provider).strip().lower(),
        api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        model=os.getenv("LLM_MODEL", settings.llm_model).strip() or settings.llm_model,
        timeout_seconds=float(
            os.getenv("LLM_TIMEOUT_SECONDS", str(settings.llm_timeout_seconds))
        ),
        max_output_tokens=int(
            os.getenv("LLM_MAX_OUTPUT_TOKENS", str(settings.llm_max_output_tokens))
        ),
    )


def create_llm_client(config: LLMConfig | None = None) -> LLMClient:
    """Return an LLM client, defaulting to disabled mode."""

    resolved = config or llm_config_from_env()
    if resolved.provider == "disabled":
        return DisabledLLMClient()
    if resolved.provider == "gemini":
        if not resolved.api_key:
            return MissingKeyLLMClient(model=resolved.model)
        return GeminiLLMClient(
            api_key=resolved.api_key,
            model=resolved.model,
            timeout_seconds=resolved.timeout_seconds,
            max_output_tokens=resolved.max_output_tokens,
        )
    return DisabledLLMClient()


def _text_from_gemini_response(payload: dict[str, Any]) -> str:
    parts = (
        (((payload.get("candidates") or [{}])[0].get("content") or {}).get("parts"))
        or []
    )
    return "\n".join(
        str(part["text"]).strip()
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ).strip()
