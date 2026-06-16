"""FakeProvider + EchoProvider — the Phase-0 and test providers.

``EchoProvider`` echoes the last user message: enough to prove
terminal → gateway → core loop → memory → reply with zero setup.

``FakeProvider`` returns a scripted sequence of ``ProviderResponse``s, so a loop
test can assert: given input X and scripted tool result Y, the loop calls the
right tool, feeds the result back, and replies Z. This is the load-bearing test
seam (build-plan §5) — deterministic, no network, no cost.

Both implement ``stream`` (the ``SupportsStreaming`` contract) so the streaming
path has a hermetic provider to test against.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from open_nexus.contracts.message import Message, Role
from open_nexus.contracts.provider import ProviderCapabilities, ProviderResponse

# Echo/Fake genuinely support streaming (they chunk their own output), so the
# capability flag is honest.
_FAKE_CAPS = ProviderCapabilities(
    streaming=True, tool_calling=True, vision=False, json_mode=False, max_context_tokens=8192
)


def _last_user(messages: list[Message]) -> str:
    return next((m.content for m in reversed(messages) if m.role == Role.USER), "")


class EchoProvider:
    name = "echo"
    capabilities = _FAKE_CAPS

    async def complete(
        self, *, system: str, messages: list[Message], tools: list[dict] | None = None
    ) -> ProviderResponse:
        return ProviderResponse(text=f"echo: {_last_user(messages)}")

    async def stream(
        self, *, system: str, messages: list[Message], tools: list[dict] | None = None
    ) -> AsyncIterator[str]:
        for token in f"echo: {_last_user(messages)}".split(" "):
            yield token + " "


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

    async def stream(
        self, *, system: str, messages: list[Message], tools: list[dict] | None = None
    ) -> AsyncIterator[str]:
        resp = await self.complete(system=system, messages=messages, tools=tools)
        for token in resp.text.split(" "):
            yield token + " "
