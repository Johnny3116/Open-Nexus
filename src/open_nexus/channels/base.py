"""Thin convenience base for channel adapters.

The authoritative ``Channel`` protocol lives in ``contracts.channel`` — adapters
satisfy it structurally. This base just carries the channel name. Channels stay
dumb: no auth, no sessions, no model knowledge.
"""

from __future__ import annotations


class BaseChannel:
    name: str = "base"
