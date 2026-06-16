"""Anthropic provider adapter (the Phase-0 default).

Translates the internal message format to/from the Anthropic Messages API.
Requires the `anthropic` extra: `pip install -e .[anthropic]`.
"""

from __future__ import annotations

from nexus.providers.base import Provider, ProviderResponse


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, *, api_key: str, model: str) -> None:
        self.model = model
        self._api_key = api_key
        # TODO(phase-0): self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(self, *, system, messages, tools=None) -> ProviderResponse:
        # TODO(phase-0): call Messages API, map content blocks -> text and
        # tool_use blocks -> ToolCall, return a ProviderResponse.
        raise NotImplementedError("AnthropicProvider.complete: Phase 0")
