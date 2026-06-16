"""OpenAI-compatible adapter (Phase 1). Requires the ``openai`` extra.

Covers OpenAI and any OpenAI-compatible endpoint by varying ``base_url``.
Imported lazily.
"""

from __future__ import annotations

from open_nexus.contracts.message import Message
from open_nexus.contracts.provider import ProviderCapabilities, ProviderResponse
from open_nexus.contracts.tool import ToolCall
from open_nexus.providers.base import to_chat_messages


class OpenAIProvider:
    name = "openai"
    capabilities = ProviderCapabilities(
        streaming=True, tool_calling=True, vision=True, json_mode=True, max_context_tokens=128_000
    )

    def __init__(self, *, api_key: str | None, model: str, base_url: str | None = None) -> None:
        self.model = model
        self._api_key = api_key
        self._base_url = base_url
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            import openai  # lazy

            self._client = openai.AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
        return self._client

    async def complete(
        self, *, system: str, messages: list[Message], tools: list[dict] | None = None
    ) -> ProviderResponse:
        client = self._ensure_client()
        chat = [{"role": "system", "content": system}, *to_chat_messages(messages)]
        resp = await client.chat.completions.create(
            model=self.model, messages=chat, tools=tools or None
        )
        choice = resp.choices[0].message
        calls = [
            ToolCall(id=tc.id, name=tc.function.name, arguments={"raw": tc.function.arguments})
            for tc in (choice.tool_calls or [])
        ]
        return ProviderResponse(text=choice.content or "", tool_calls=calls, raw=resp)
