"""Channel layer — one adapter per surface.

Each adapter does three jobs:
    1. normalise inbound messages into the common internal format,
    2. enforce a per-channel allowlist (who may talk to Nexus on this surface),
    3. serialise replies back out.

Channels are fully decoupled from the model and tools. This decoupling *is* the
product: swap Telegram <-> Discord <-> web, swap the model, and nothing else
changes.
"""

from nexus.channels.base import Channel, InboundMessage, OutboundMessage

__all__ = ["Channel", "InboundMessage", "OutboundMessage"]
