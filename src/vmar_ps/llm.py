from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationResponse:
    success: bool
    text: str
    model: str
    provider: str
    error: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class ModelClient:
    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
        thinking_level: str = "medium",
    ) -> GenerationResponse:
        raise NotImplementedError


class GeminiClient(ModelClient):
    provider = "google"

    def __init__(self, api_key: Optional[str] = None):
        from google import genai

        self._client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
        thinking_level: str = "medium",
    ) -> GenerationResponse:
        try:
            from google.genai import types

            kwargs = {"max_output_tokens": max_output_tokens}
            if model.startswith("gemini-3.8"):
                kwargs["thinking_config"] = types.ThinkingConfig(
                    thinking_level=thinking_level
                )
            else:
                kwargs["temperature"] = temperature

            response = self._client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(**kwargs),
            )
            usage = getattr(response, "usage_metadata", None)
            return GenerationResponse(
                success=True,
                text=getattr(response, "text", "") or "",
                model=model,
                provider=self.provider,
                input_tokens=getattr(usage, "prompt_token_count", None) if usage else None,
                output_tokens=getattr(usage, "candidates_token_count", None) if usage else None,
                total_tokens=getattr(usage, "total_token_count", None) if usage else None,
            )
        except Exception as exc:
            return GenerationResponse(
                success=False,
                text="",
                model=model,
                provider=self.provider,
                error=str(exc),
            )


def build_client(agent_config: dict) -> ModelClient:
    provider = str(agent_config.get("provider", "google")).lower()
    if provider != "google":
        raise ValueError(f"Unsupported provider: {provider}")
    api_key = os.getenv(str(agent_config.get("api_key_env", "GEMINI_API_KEY")))
    return GeminiClient(api_key=api_key)
