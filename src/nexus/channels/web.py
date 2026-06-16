"""Web UI channel — FastAPI + WebSocket.

The desktop widget talks to Core over this same WebSocket. Requires the `web`
extra. Clients connect to Core; they never touch Supabase or providers directly.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from nexus.channels.base import Channel, InboundMessage, OutboundMessage


class WebChannel(Channel):
    name = "web"

    def __init__(self, *, host: str = "127.0.0.1", port: int = 8800, allowlist=None) -> None:
        super().__init__(allowlist=allowlist)
        self.host = host
        self.port = port
        # TODO(phase-1): build a FastAPI app with a /ws endpoint.

    async def listen(self) -> AsyncIterator[InboundMessage]:
        raise NotImplementedError("WebChannel.listen: Phase 1")
        yield  # pragma: no cover

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        raise NotImplementedError("WebChannel.send: Phase 1")
