"""Outbound — serialise a core reply back to the originating channel."""

from __future__ import annotations

from open_nexus.contracts.channel import Channel, OutboundMessage


async def send_reply(channel: Channel, *, channel_user_id: str, text: str) -> None:
    await channel.send(channel_user_id, OutboundMessage(text=text))
