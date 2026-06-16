"""Telegram channel — the first *real* channel (Phase 1).

Uses aiogram (or python-telegram-bot). Requires the `telegram` extra. Enforces
the per-channel allowlist strictly: only configured user ids may talk to Nexus.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from nexus.channels.base import Channel, InboundMessage, OutboundMessage


class TelegramChannel(Channel):
    name = "telegram"

    def __init__(self, *, token: str, allowlist=None) -> None:
        super().__init__(allowlist=allowlist)
        self._token = token
        # TODO(phase-1): bot = aiogram.Bot(token); register a message handler.

    async def listen(self) -> AsyncIterator[InboundMessage]:
        raise NotImplementedError("TelegramChannel.listen: Phase 1")
        yield  # pragma: no cover

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        raise NotImplementedError("TelegramChannel.send: Phase 1")
