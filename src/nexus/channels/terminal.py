"""Terminal channel — the Phase-0 surface (trivial, no external deps).

Reads from stdin, writes to stdout. The single local user is implicitly allowed.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from nexus.channels.base import Channel, InboundMessage, OutboundMessage

LOCAL_USER_ID = "local"


class TerminalChannel(Channel):
    name = "terminal"

    def __init__(self) -> None:
        # The local operator is trusted on the terminal surface.
        super().__init__(allowlist=[LOCAL_USER_ID])

    async def listen(self) -> AsyncIterator[InboundMessage]:
        # TODO(phase-0): async stdin read loop yielding InboundMessage(text=line).
        raise NotImplementedError("TerminalChannel.listen: Phase 0")
        yield  # pragma: no cover  (makes this an async generator)

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        print(f"nexus> {message.text}")
