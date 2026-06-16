"""OpenAI-compatible provider adapter.

Covers OpenAI itself, OpenRouter, and any OpenAI-compatible endpoint, by varying
``base_url``. Requires the `openai` extra.
"""

from __future__ import annotations

from nexus.providers.base import Provider, ProviderResponse


class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self, *, api_key: str | None, model: str, base_url: str | None = None) -> None:
        self.model = model
        self._api_key = api_key
        self._base_url = base_url
        # TODO(phase-1): self._client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def complete(self, *, system, messages, tools=None) -> ProviderResponse:
        # TODO(phase-1): chat.completions with tools; map tool_calls -> ToolCall.
        raise NotImplementedError("OpenAIProvider.complete: Phase 1")
