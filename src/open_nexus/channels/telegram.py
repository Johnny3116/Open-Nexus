"""Telegram channel (Phase 5) — first real remote channel. ``telegram`` extra.

A dumb adapter: normalise updates → InboundMessage, send replies out. The
per-user allowlist is enforced by the gateway's auth, not here.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from open_nexus.channels.base import BaseChannel
from open_nexus.contracts.channel import InboundMessage, OutboundMessage


class TelegramChannel(BaseChannel):
    name = "telegram"

    def __init__(self, *, token: str) -> None:
        self._token = token

    async def listen(self) -> AsyncIterator[InboundMessage]:
        raise NotImplementedError("TelegramChannel.listen: Phase 5")
        yield  # pragma: no cover

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        raise NotImplementedError("TelegramChannel.send: Phase 5")
