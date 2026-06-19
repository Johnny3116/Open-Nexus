"""OpenAI-compatible adapter (Phase 1). Requires the ``openai`` extra.

Covers OpenAI and any OpenAI-compatible endpoint by varying ``base_url``.
Imported lazily.
"""

from __future__ import annotations

import json

from open_nexus.contracts.message import Message
from open_nexus.contracts.provider import ProviderCapabilities, ProviderResponse
from open_nexus.contracts.tool import ToolCall
from open_nexus.providers.base import to_chat_messages


def _parse_arguments(raw: str | None) -> dict:
    """OpenAI returns tool arguments as a JSON string; parse to a dict.

    Falls back to wrapping the raw text if the model emitted invalid JSON, so a
    malformed argument string degrades instead of crashing.
    """
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    return parsed if isinstance(parsed, dict) else {"raw": raw}


class OpenAIProvider:
    name = "openai"
    capabilities = ProviderCapabilities(
        streaming=True, tool_calling=True, vision=True, json_mode=True, max_context_tokens=128_000
    )

    def __init__(
        self, *, api_key: str | None, model: str, base_url: str | None = None, client=None
    ) -> None:
        self.model = model
        self._api_key = api_key
        self._base_url = base_url
        # Injected client → network-free translation tests; else built lazily.
        self._client = client

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
            ToolCall(
                id=tc.id,
                name=tc.function.name,
                arguments=_parse_arguments(tc.function.arguments),
            )
            for tc in (choice.tool_calls or [])
        ]
        return ProviderResponse(text=choice.content or "", tool_calls=calls, raw=resp)
