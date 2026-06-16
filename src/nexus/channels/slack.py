"""Slack channel (last by effort). Uses Slack Bolt; `slack` extra."""

from __future__ import annotations

from collections.abc import AsyncIterator

from nexus.channels.base import Channel, InboundMessage, OutboundMessage


class SlackChannel(Channel):
    name = "slack"

    def __init__(self, *, bot_token: str, app_token: str, allowlist=None) -> None:
        super().__init__(allowlist=allowlist)
        self._bot_token = bot_token
        self._app_token = app_token
        # TODO(phase-2+): Bolt app in socket mode with a message handler.

    async def listen(self) -> AsyncIterator[InboundMessage]:
        raise NotImplementedError("SlackChannel.listen: later phase")
        yield  # pragma: no cover

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        raise NotImplementedError("SlackChannel.send: later phase")
