"""Provider interface + the one internal message format.

All providers speak this shape; adapters translate to/from the vendor API. This
is what keeps the personality in the harness rather than the model: the Core
never sees a vendor-specific request.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A tool invocation requested by the model, in internal form."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ProviderResponse:
    """Normalised model response."""

    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any = None


class Provider(abc.ABC):
    """A model backend. Anthropic, OpenAI, OpenRouter, local — all look alike."""

    name: str

    @abc.abstractmethod
    async def complete(
        self,
        *,
        system: str,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> ProviderResponse:
        """Run one completion and return a normalised ProviderResponse."""


class FallbackProvider(Provider):
    """Wraps an ordered list of providers with exponential-backoff failover."""

    name = "fallback"

    def __init__(self, providers: list[Provider]) -> None:
        if not providers:
            raise ValueError("FallbackProvider needs at least one provider")
        self._providers = providers

    async def complete(self, **kwargs) -> ProviderResponse:  # type: ignore[override]
        # TODO(phase-1): try each in order; on transient error back off
        # (2s, 4s, 8s, 16s) and move to the next. Surface the last error if all fail.
        raise NotImplementedError("FallbackProvider.complete: Phase 1")
