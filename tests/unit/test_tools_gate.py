"""Tools run through the loop, and the safety gate blocks irreversible ones."""

from __future__ import annotations

from open_nexus.contracts.provider import ProviderResponse
from open_nexus.contracts.tool import RiskLevel, ToolCall, ToolManifest
from open_nexus.core.loop import run_turn
from open_nexus.providers.fake import FakeProvider
from open_nexus.safety.approval import ApprovalGate
from open_nexus.tools.base import Tool
from open_nexus.tools.registry import ToolRegistry


def _registry(*, confirmer=None) -> ToolRegistry:
    reg = ToolRegistry(gate=ApprovalGate(confirmer=confirmer))
    reg.register(
        Tool(
            manifest=ToolManifest(name="clock", description="time", risk_level=RiskLevel.READ),
            handler=lambda **_: _async("12:00"),
        )
    )
    reg.register(
        Tool(
            manifest=ToolManifest(name="rm", description="delete", risk_level=RiskLevel.WRITE),
            handler=lambda **_: _async("deleted"),
        )
    )
    return reg


async def _async(value):
    return value


async def test_read_tool_runs_without_approval(store, assembler, state):
    provider = FakeProvider(
        [
            ProviderResponse(tool_calls=[ToolCall(id="1", name="clock", arguments={})]),
            ProviderResponse(text="it is 12:00"),
        ]
    )
    reply = await run_turn(
        user_text="time?",
        state=state,
        provider=provider,
        assembler=assembler,
        store=store,
        tools=_registry(),
    )
    assert reply == "it is 12:00"


async def test_write_tool_denied_by_default():
    # WRITE risk + no confirmer => fail closed.
    reg = _registry()
    result = await reg.run(ToolCall(id="1", name="rm", arguments={}))
    assert result == {"error": "denied by approval gate", "tool": "rm"}


async def test_write_tool_runs_when_confirmed():
    async def yes(_req):
        return True

    reg = _registry(confirmer=yes)
    result = await reg.run(ToolCall(id="1", name="rm", arguments={}))
    assert result == "deleted"
