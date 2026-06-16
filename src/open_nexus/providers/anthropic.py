"""Anthropic adapter (Phase 1). Requires the ``anthropic`` extra.

Imported lazily so Phase 0 / unit tests never need the SDK or a key.
"""

from __future__ import annotations

from open_nexus.contracts.message import Message
from open_nexus.contracts.provider import ProviderCapabilities, ProviderResponse
from open_nexus.contracts.tool import ToolCall
from open_nexus.providers.base import to_chat_messages


class AnthropicProvider:
    name = "anthropic"
    capabilities = ProviderCapabilities(
        streaming=True, tool_calling=True, vision=True, json_mode=False, max_context_tokens=200_000
    )

    def __init__(self, *, api_key: str, model: str) -> None:
        self.model = model
        self._api_key = api_key
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            import anthropic  # lazy

            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
        return self._client

    async def complete(
        self, *, system: str, messages: list[Message], tools: list[dict] | None = None
    ) -> ProviderResponse:
        client = self._ensure_client()
        resp = await client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system,
            messages=to_chat_messages(messages),
            tools=tools or [],
        )
        text: list[str] = []
        calls: list[ToolCall] = []
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                text.append(block.text)
            elif getattr(block, "type", None) == "tool_use":
                calls.append(ToolCall(id=block.id, name=block.name, arguments=block.input))
        return ProviderResponse(text="".join(text), tool_calls=calls, raw=resp)
