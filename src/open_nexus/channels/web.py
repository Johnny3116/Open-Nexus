"""Web channel — FastAPI + WebSocket (Phase 2). Requires the ``web`` extra.

The desktop widget connects over this same WebSocket. Stub for now; the API
surface is sketched in ``open_nexus.api.server``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from open_nexus.channels.base import BaseChannel
from open_nexus.contracts.channel import InboundMessage, OutboundMessage


class WebChannel(BaseChannel):
    name = "web"

    async def listen(self) -> AsyncIterator[InboundMessage]:
        raise NotImplementedError("WebChannel.listen: Phase 2")
        yield  # pragma: no cover

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        raise NotImplementedError("WebChannel.send: Phase 2")
