"""Core loop: input → context → provider → reply → stored."""

from __future__ import annotations

from open_nexus.contracts.message import Role
from open_nexus.contracts.provider import ProviderResponse
from open_nexus.core.loop import run_turn
from open_nexus.providers.fake import EchoProvider, FakeProvider


async def test_echo_turn_stores_both_messages(store, assembler, state):
    reply = await run_turn(
        user_text="hello", state=state, provider=EchoProvider(), assembler=assembler, store=store
    )
    assert reply == "echo: hello"
    history = store.recent(session_id=state.session_id)
    assert [(m.role, m.content) for m in history] == [
        (Role.USER, "hello"),
        (Role.ASSISTANT, "echo: hello"),
    ]


async def test_scripted_provider_reply(store, assembler, state):
    provider = FakeProvider([ProviderResponse(text="scripted answer")])
    reply = await run_turn(
        user_text="x", state=state, provider=provider, assembler=assembler, store=store
    )
    assert reply == "scripted answer"


async def test_system_prompt_carries_identity(store, assembler, state):
    ctx = assembler.assemble(session_id=state.session_id, store=store, user_text="hi")
    assert "You are Nexus." in ctx.system
