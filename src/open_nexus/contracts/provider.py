"""Provider contracts — the seam that makes "any AI/API" real.

The core loop talks only to this ``Provider`` protocol. Real adapters translate
their vendor API to/from these types; tests inject a ``FakeProvider``. Adding a
new model means adding an adapter + config, never touching the core loop.

``ProviderCapabilities`` lets the router make sane choices (vision request → a
vision-capable provider; cheap summary → local).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel

from open_nexus.contracts.message import Message
from open_nexus.contracts.tool import ToolCall


class ProviderCapabilities(BaseModel):
    """What a given model/provider can do. Declared per adapter, from day one."""

    streaming: bool = False
    tool_calling: bool = False
    vision: bool = False
    json_mode: bool = False
    system_prompt: bool = True
    max_context_tokens: int = 8192


class ProviderResponse(BaseModel):
    """Normalised model response: text and/or tool calls."""

    text: str = ""
    tool_calls: list[ToolCall] = []
    # Raw vendor payload, kept for debugging. Excluded from equality/serialisation.
    raw: Any = None


@runtime_checkable
class Provider(Protocol):
    """A model backend. Anthropic, OpenAI, local, Fake — all look alike to Core."""

    name: str
    capabilities: ProviderCapabilities

    async def complete(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> ProviderResponse:
        """Run one completion and return a normalised ProviderResponse."""
        ...


@runtime_checkable
class SupportsStreaming(Protocol):
    """Optional capability: yield text chunks as they arrive.

    A provider advertises this via ``capabilities.streaming`` and implements
    ``stream``. The loop/API can prefer it when streaming output is wanted; code
    that needs a single answer just calls ``complete``.
    """

    def stream(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> AsyncIterator[str]:
        """Yield response text incrementally."""
        ...
