"""Gateway: auth + inbound resolution, plus an end-to-end echo through a channel."""

from __future__ import annotations

import pytest

from open_nexus.channels.base import BaseChannel
from open_nexus.contracts.channel import InboundMessage, OutboundMessage
from open_nexus.core.session import SessionRegistry
from open_nexus.gateway.auth import Allowlist
from open_nexus.gateway.inbound import Rejected, resolve_inbound
from open_nexus.gateway.router import Gateway
from open_nexus.memory.sqlite_store import SQLiteStore
from open_nexus.providers.fake import EchoProvider


def test_terminal_is_trusted():
    assert Allowlist().is_allowed("terminal", "local")


def test_unknown_user_rejected_on_remote_channel():
    msg = InboundMessage(channel="telegram", channel_user_id="999", text="hi")
    with pytest.raises(Rejected):
        resolve_inbound(msg, allowlist=Allowlist(), sessions=SessionRegistry(), active_model="echo")


def test_allowed_user_resolves_state():
    allow = Allowlist()
    allow.allow("telegram", "42")
    msg = InboundMessage(channel="telegram", channel_user_id="42", text="hi")
    state = resolve_inbound(msg, allowlist=allow, sessions=SessionRegistry(), active_model="echo")
    assert state.active_channel == "telegram"
    assert state.user_id == "42"


class _ScriptedChannel(BaseChannel):
    name = "terminal"

    def __init__(self, lines):
        self._lines = lines
        self.sent: list[str] = []

    async def listen(self):
        for line in self._lines:
            yield InboundMessage(channel=self.name, channel_user_id="local", text=line)

    async def send(self, channel_user_id, message: OutboundMessage):
        self.sent.append(message.text)


async def test_gateway_drives_channel_end_to_end():
    channel = _ScriptedChannel(["hello"])
    gateway = Gateway(provider=EchoProvider(), store=SQLiteStore(":memory:"), active_model="echo")
    await gateway.run(channel)
    assert channel.sent == ["echo: hello"]
