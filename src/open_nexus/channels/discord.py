"""Discord channel (Phase 5). Requires the ``discord`` extra.

Dumb adapter: normalise messages → InboundMessage, send replies out. Allowlist is
enforced by the gateway. (Preferred over Slack for this project.)
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from open_nexus.channels.base import BaseChannel
from open_nexus.contracts.channel import InboundMessage, OutboundMessage


class DiscordChannel(BaseChannel):
    name = "discord"

    def __init__(self, *, token: str) -> None:
        self._token = token

    async def listen(self) -> AsyncIterator[InboundMessage]:
        raise NotImplementedError("DiscordChannel.listen: Phase 5")
        yield  # pragma: no cover

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        raise NotImplementedError("DiscordChannel.send: Phase 5")
