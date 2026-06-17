"""Phase 3 safety proof: unsafe tools cannot execute without approval.

Covers the registry directly, the ToolRun audit log, and an end-to-end turn
through the Gateway where a model-requested write is blocked until approved.
"""

from __future__ import annotations

import asyncio

from open_nexus.contracts.channel import InboundMessage
from open_nexus.contracts.provider import ProviderResponse
from open_nexus.contracts.tool import ToolCall, ToolRun, ToolRunStatus
from open_nexus.gateway.router import Gateway
from open_nexus.memory.sqlite_store import SQLiteStore
from open_nexus.providers.fake import FakeProvider
from open_nexus.safety.approval import ApprovalGate
from open_nexus.safety.approval_manager import ApprovalManager
from open_nexus.tools.demo import clock_tool, write_note_tool
from open_nexus.tools.registry import ToolRegistry


async def _wait_pending(m: ApprovalManager) -> None:
    for _ in range(1000):
        if m.pending():
            return
        await asyncio.sleep(0)
    raise AssertionError("nothing became pending")


# --- registry level ---------------------------------------------------------


async def test_read_only_tool_runs_without_approval():
    reg = ToolRegistry()  # default gate denies gated actions, but READ isn't gated
    reg.register(clock_tool())
    result = await reg.run(ToolCall(id="1", name="clock"))
    assert "utc" in result


async def test_write_tool_denied_without_confirmer():
    reg = ToolRegistry()  # no confirmer → fail closed
    reg.register(write_note_tool())
    result = await reg.run(
        ToolCall(id="1", name="write_note", arguments={"key": "k", "value": "v"})
    )
    assert result == {"error": "denied by approval gate", "tool": "write_note"}


async def test_write_tool_runs_only_after_approval():
    m = ApprovalManager()
    notes: dict[str, str] = {}
    reg = ToolRegistry(gate=ApprovalGate(confirmer=m.confirm))
    reg.register(write_note_tool(notes))

    call = ToolCall(id="1", name="write_note", arguments={"key": "k", "value": "v"})
    task = asyncio.create_task(reg.run(call))
    await _wait_pending(m)
    assert notes == {}  # nothing written while awaiting approval
    assert m.approve(m.pending()[0].id)
    assert await task == {"written": "k"}
    assert notes == {"k": "v"}


# --- audit log --------------------------------------------------------------


async def test_tool_run_logged_ok():
    store = SQLiteStore(":memory:")
    reg = ToolRegistry()
    reg.register(clock_tool())
    await reg.run(ToolCall(id="1", name="clock"), store=store, session_id="s")
    history = store.recent(session_id="s")
    assert len(history) == 1
    run = ToolRun.model_validate_json(history[0].content)
    assert run.tool_name == "clock" and run.status == ToolRunStatus.OK


async def test_denied_run_logged():
    store = SQLiteStore(":memory:")
    reg = ToolRegistry()
    reg.register(write_note_tool())
    await reg.run(
        ToolCall(id="1", name="write_note", arguments={"key": "k", "value": "v"}),
        store=store,
        session_id="s",
    )
    run = ToolRun.model_validate_json(store.recent(session_id="s")[0].content)
    assert run.status == ToolRunStatus.DENIED


# --- end to end through the Gateway -----------------------------------------


async def test_gateway_turn_blocks_write_until_approved():
    m = ApprovalManager()
    notes: dict[str, str] = {}
    reg = ToolRegistry(gate=ApprovalGate(confirmer=m.confirm))
    reg.register(write_note_tool(notes))
    provider = FakeProvider(
        [
            ProviderResponse(
                tool_calls=[
                    ToolCall(id="1", name="write_note", arguments={"key": "k", "value": "v"})
                ]
            ),
            ProviderResponse(text="done"),
        ]
    )
    gw = Gateway(
        provider=provider,
        store=SQLiteStore(":memory:"),
        tools=reg,
        approvals=m,
        active_model="fake",
    )
    msg = InboundMessage(channel="terminal", channel_user_id="local", text="write k=v")

    task = asyncio.create_task(gw.handle(msg))
    await _wait_pending(m)
    assert notes == {}  # blocked: the model wanted it, the gate held it
    assert m.approve(m.pending()[0].id)

    reply, _ = await task
    assert reply == "done"
    assert notes == {"k": "v"}
