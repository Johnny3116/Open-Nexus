"""Local / Ollama adapter (Phase 1) — OpenAI-compatible, just a base_url.

Ollama exposes an OpenAI-compatible API, so cloud and local look identical to
Core. No API key required. Reuses ``OpenAIProvider`` with smaller declared caps.
"""

from __future__ import annotations

from open_nexus.contracts.provider import ProviderCapabilities
from open_nexus.providers.openai import OpenAIProvider


class LocalProvider(OpenAIProvider):
    name = "local"
    capabilities = ProviderCapabilities(
        streaming=True, tool_calling=False, vision=False, json_mode=True, max_context_tokens=32_000
    )

    def __init__(self, *, base_url: str, model: str) -> None:
        super().__init__(api_key=None, model=model, base_url=base_url)
