"""Provider router: fallback chain + capability-aware selection."""

from __future__ import annotations

from open_nexus.contracts.provider import ProviderCapabilities, ProviderResponse
from open_nexus.providers.router import ProviderRouter


class _Boom:
    name = "boom"
    capabilities = ProviderCapabilities(tool_calling=False, vision=False)

    async def complete(self, *, system, messages, tools=None):
        raise RuntimeError("provider down")


class _Ok:
    name = "ok"
    capabilities = ProviderCapabilities(tool_calling=True, vision=True)

    async def complete(self, *, system, messages, tools=None):
        return ProviderResponse(text="from ok")


async def test_failover_to_next_provider():
    router = ProviderRouter(
        providers={"boom": _Boom(), "ok": _Ok()},
        default="boom",
        fallback=["ok"],
        base_backoff=0,  # no real sleep in tests
    )
    resp = await router.complete(system="s", messages=[])
    assert resp.text == "from ok"


def test_capability_selection_skips_incapable_default():
    router = ProviderRouter(
        providers={"boom": _Boom(), "ok": _Ok()}, default="boom", fallback=["ok"]
    )
    # boom lacks vision; selection should fall through to ok.
    assert router.select(requires_vision=True) == "ok"
