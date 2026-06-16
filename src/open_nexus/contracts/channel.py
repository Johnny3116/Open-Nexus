"""Channel contracts — dumb adapters in, dumb adapters out.

Channels do exactly three things: normalise inbound platform payloads into an
``InboundMessage``, and serialise an ``OutboundMessage`` back out. They do NOT
know about sessions, auth, the model, or tools — the gateway owns all of that.
Core must not know Discord/Telegram/terminal/web exist.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class InboundMessage(BaseModel):
    """A normalised message arriving from any channel."""

    channel: str
    channel_user_id: str  # platform-native id
    text: str
    raw: Any = None  # original payload (attachments, etc.)


class OutboundMessage(BaseModel):
    """A reply to serialise back out to a channel."""

    text: str
    # Optional declarative cues (e.g. VTube avatar): {"emotion": "amused"}.
    cues: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class Channel(Protocol):
    """A surface Open-Nexus can talk on. Knows nothing about the core."""

    name: str

    def listen(self) -> AsyncIterator[InboundMessage]:
        """Yield normalised inbound messages."""
        ...

    async def send(self, channel_user_id: str, message: OutboundMessage) -> None:
        """Serialise a reply back out to the channel."""
        ...
