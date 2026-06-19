"""Regression tests for the runtime-hardening fixes.

Each test here fails against the pre-fix code:
  - duplicate current user message in the prompt,
  - tool-audit rows leaking into replayed context,
  - a raising tool / failing provider crashing the channel,
  - a hung provider wedging the session.
"""

from __future__ import annotations

import asyncio

from open_nexus.channels.base import BaseChannel
from open_nexus.contracts.channel import InboundMessage, OutboundMessage
from open_nexus.contracts.message import Role
from open_nexus.contracts.provider import ProviderCapabilities, ProviderResponse
from open_nexus.contracts.tool import RiskLevel, ToolCall, ToolManifest
from open_nexus.core.loop import run_turn
from open_nexus.gateway.router import Gateway
from open_nexus.memory.sqlite_store import SQLiteStore
from open_nexus.providers.fake import FakeProvider
from open_nexus.tools.base import Tool
from open_nexus.tools.registry import ToolRegistry

_CAPS = ProviderCapabilities(tool_calling=True)


class RecordingProvider:
    """Captures the exact message list it is asked to complete."""

    name = "rec"
    capabilities = _CAPS

    def __init__(self) -> None:
        self.calls: list[list] = []

    async def complete(self, *, system, messages, tools=None) -> ProviderResponse:
        self.calls.append(list(messages))
        return ProviderResponse(text="ok")


class _ScriptedChannel(BaseChannel):
    name = "terminal"

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines
        self.sent: list[str] = []

    async def listen(self):
        for line in self._lines:
            yield InboundMessage(channel=self.name, channel_user_id="local", text=line)

    async def send(self, channel_user_id, message: OutboundMessage) -> None:
        self.sent.append(message.text)


# --- #2 duplicate user message ----------------------------------------------


async def test_user_message_not_duplicated(store, assembler, state):
    provider = RecordingProvider()
    await run_turn(
        user_text="hello", state=state, provider=provider, assembler=assembler, store=store
    )
    sent = provider.calls[0]
    assert [m.content for m in sent if m.role == Role.USER] == ["hello"]


async def test_history_has_no_duplicates_across_turns(store, assembler, state):
    provider = RecordingProvider()
    for text in ("one", "two"):
        await run_turn(
            user_text=text, state=state, provider=provider, assembler=assembler, store=store
        )
    second_call = provider.calls[1]
    user_contents = [m.content for m in second_call if m.role == Role.USER]
    assert user_contents == ["one", "two"]  # each exactly once, in order


# --- #3 tool-audit rows excluded from replayed context ----------------------


def test_assemble_excludes_tool_audit_rows(assembler, state):
    store = SQLiteStore(":memory:")
    store.append_message(session_id=state.session_id, role=Role.USER, content="hi")
    store.append_message(
        session_id=state.session_id,
        role=Role.TOOL,
        content='{"status":"ok","risk_level":"shell"}',
        tool_name="clock",
    )
    ctx = assembler.assemble(session_id=state.session_id, store=store, user_text="next")
    assert all(m.role != Role.TOOL for m in ctx.messages)


# --- #1 a raising tool / failing provider must not crash the channel --------


async def test_channel_survives_a_raising_tool():
    async def boom() -> dict:
        raise RuntimeError("kaboom")

    reg = ToolRegistry()
    reg.register(Tool(manifest=ToolManifest(name="boom", risk_level=RiskLevel.READ), handler=boom))
    provider = FakeProvider(
        [
            ProviderResponse(tool_calls=[ToolCall(id="1", name="boom", arguments={})]),
            ProviderResponse(text="recovered"),
        ]
    )
    channel = _ScriptedChannel(["go"])
    gw = Gateway(provider=provider, store=SQLiteStore(":memory:"), tools=reg, active_model="fake")
    await gw.run(channel)  # must not raise
    assert channel.sent == ["recovered"]


async def test_channel_survives_failing_provider_and_keeps_serving():
    class _AlwaysFails:
        name = "x"
        capabilities = _CAPS

        async def complete(self, *, system, messages, tools=None):
            raise RuntimeError("provider down")

    channel = _ScriptedChannel(["first", "second"])
    gw = Gateway(provider=_AlwaysFails(), store=SQLiteStore(":memory:"), active_model="x")
    await gw.run(channel)  # must not raise
    assert len(channel.sent) == 2  # both messages got a (graceful) reply
    assert all("went wrong" in s for s in channel.sent)


# --- #4 hung provider degrades instead of wedging ---------------------------


async def test_provider_timeout_returns_gracefully(store, assembler, state):
    class _Slow:
        name = "slow"
        capabilities = _CAPS

        async def complete(self, *, system, messages, tools=None):
            await asyncio.sleep(10)
            return ProviderResponse(text="late")

    reply = await run_turn(
        user_text="hi",
        state=state,
        provider=_Slow(),
        assembler=assembler,
        store=store,
        request_timeout=0.01,
    )
    assert "didn't respond in time" in reply
