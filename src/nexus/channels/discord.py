"""Discord channel (later than Telegram). Uses discord.py; `discord` extra."""

from __future__ import annotations

from collections.abc import AsyncIterator

from nexus.channels.base import Channel, InboundMessage, OutboundMessage


class DiscordChannel(Channel):
    name = "discord"

    def __init__(self, *, token: str, allowlist=None) -> None:
        super().__init__(allowlist=allowlist)
        self._token = token
        # TODO(phase-2+): discord.Client with an on_message handler.

    async def listen(self) -> AsyncIterator[InboundMessage]:
        raise NotImplementedError("DiscordChannel.listen: later phase")
        yield  # pragma: no cover

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        raise NotImplementedError("DiscordChannel.send: later phase")
