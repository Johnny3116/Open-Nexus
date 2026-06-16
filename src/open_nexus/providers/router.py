"""ProviderRouter — config-driven selection + capability routing + fallback.

Adding a new AI/API should require an adapter + config, not a core-loop change.
The router owns:
  - the default provider and an ordered fallback chain,
  - capability-aware selection (vision → a vision provider; cheap → local),
  - exponential-backoff failover when a provider errors.
"""

from __future__ import annotations

import asyncio

from open_nexus.contracts.message import Message
from open_nexus.contracts.provider import Provider, ProviderResponse
from open_nexus.observability.logger import get_logger

_log = get_logger("open_nexus.providers.router")


class ProviderRouter:
    def __init__(
        self,
        *,
        providers: dict[str, Provider],
        default: str,
        fallback: list[str] | None = None,
        base_backoff: float = 2.0,
    ) -> None:
        if default not in providers:
            raise ValueError(f"default provider {default!r} not in providers")
        self._providers = providers
        self._default = default
        # Chain always starts with the default, then configured fallbacks.
        self._chain = [default, *[p for p in (fallback or []) if p != default]]
        self._base_backoff = base_backoff

    def get(self, name: str) -> Provider:
        return self._providers[name]

    def select(self, *, requires_vision: bool = False, requires_tools: bool = False) -> str:
        """Pick the first chain provider whose capabilities satisfy the need."""
        for name in self._chain:
            caps = self._providers[name].capabilities
            if requires_vision and not caps.vision:
                continue
            if requires_tools and not caps.tool_calling:
                continue
            return name
        return self._default

    async def complete(
        self, *, system: str, messages: list[Message], tools: list[dict] | None = None
    ) -> ProviderResponse:
        """Try the chain in order; back off exponentially and fail over on error."""
        last_exc: Exception | None = None
        for attempt, name in enumerate(self._chain):
            try:
                return await self._providers[name].complete(
                    system=system, messages=messages, tools=tools
                )
            except Exception as exc:  # noqa: BLE001 - failover is the whole point
                last_exc = exc
                _log.warning("provider %s failed (%s); failing over", name, exc)
                if attempt < len(self._chain) - 1:
                    await asyncio.sleep(self._base_backoff * (2**attempt))
        raise RuntimeError("all providers in the fallback chain failed") from last_exc
