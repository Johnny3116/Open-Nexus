"""Local provider (Ollama / llama.cpp) — OpenAI-compatible endpoint.

Ollama exposes an OpenAI-compatible API, so cloud and local look identical to
Core. Point ``base_url`` at the local server (e.g. http://localhost:11434/v1).
No API key required.
"""

from __future__ import annotations

from nexus.providers.openai import OpenAIProvider


class LocalProvider(OpenAIProvider):
    name = "local"

    def __init__(self, *, base_url: str, model: str) -> None:
        super().__init__(api_key=None, model=model, base_url=base_url)
