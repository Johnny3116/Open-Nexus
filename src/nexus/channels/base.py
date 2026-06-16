"""Channel interface + common inbound/outbound message shapes."""

from __future__ import annotations

import abc
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class InboundMessage:
    """A normalised message arriving from any channel."""

    channel: str
    channel_user_id: str
    text: str
    # Raw platform payload kept for channel-specific needs (attachments, etc.).
    raw: object = None


@dataclass
class OutboundMessage:
    """A reply to serialise back out to a channel."""

    text: str
    # Optional declarative cues (e.g. for the VTube avatar): {"emotion": "amused"}.
    cues: dict | None = None


class Channel(abc.ABC):
    """A surface Nexus can talk on. Decoupled from model and tools."""

    name: str

    def __init__(self, *, allowlist: list[str] | None = None) -> None:
        # Per-channel allowlist of platform-native user ids permitted to talk.
        self.allowlist = set(allowlist or [])

    def is_allowed(self, channel_user_id: str) -> bool:
        """Allowlist check. Empty allowlist == deny-all by default (safer)."""
        return channel_user_id in self.allowlist

    @abc.abstractmethod
    async def listen(self) -> AsyncIterator[InboundMessage]:
        """Yield normalised inbound messages."""
        raise NotImplementedError

    @abc.abstractmethod
    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        """Serialise a reply back out to the channel."""
        raise NotImplementedError
