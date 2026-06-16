"""OpenRouter provider — OpenAI-compatible, just a different base_url.

Kept as a thin alias so config can name it explicitly. OpenRouter exposes the
OpenAI API shape, so it reuses OpenAIProvider under the hood.
"""

from __future__ import annotations

from nexus.providers.openai import OpenAIProvider

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider(OpenAIProvider):
    name = "openrouter"

    def __init__(self, *, api_key: str, model: str) -> None:
        super().__init__(api_key=api_key, model=model, base_url=OPENROUTER_BASE_URL)
