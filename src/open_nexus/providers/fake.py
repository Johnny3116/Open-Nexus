"""FakeProvider + EchoProvider — the Phase-0 and test providers.

``EchoProvider`` echoes the last user message: enough to prove
terminal → gateway → core loop → memory → reply with zero setup.

``FakeProvider`` returns a scripted sequence of ``ProviderResponse``s, so a loop
test can assert: given input X and scripted tool result Y, the loop calls the
right tool, feeds the result back, and replies Z. This is the load-bearing test
seam (build-plan §5) — deterministic, no network, no cost.
"""

from __future__ import annotations

from open_nexus.contracts.message import Message, Role
from open_nexus.contracts.provider import ProviderCapabilities, ProviderResponse

_FAKE_CAPS = ProviderCapabilities(
    streaming=False, tool_calling=True, vision=False, json_mode=False, max_context_tokens=8192
)


class EchoProvider:
    name = "echo"
    capabilities = _FAKE_CAPS

    async def complete(
        self, *, system: str, messages: list[Message], tools: list[dict] | None = None
    ) -> ProviderResponse:
        last_user = next((m.content for m in reversed(messages) if m.role == Role.USER), "")
        return ProviderResponse(text=f"echo: {last_user}")


class FakeProvider:
    """Returns pre-scripted responses, one per ``complete`` call."""

    name = "fake"
    capabilities = _FAKE_CAPS

    def __init__(self, script: list[ProviderResponse]) -> None:
        self._script = iter(script)

    async def complete(
        self, *, system: str, messages: list[Message], tools: list[dict] | None = None
    ) -> ProviderResponse:
        try:
            return next(self._script)
        except StopIteration as exc:  # pragma: no cover - misuse guard
            raise AssertionError("FakeProvider script exhausted") from exc
