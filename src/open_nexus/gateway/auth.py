"""Auth — per-channel allowlist. Fail closed."""

from __future__ import annotations


class Allowlist:
    """Who may talk to Nexus on each channel.

    An empty allowlist for a channel means deny-all (safer default). The terminal
    channel is trusted by convention (local operator) unless overridden.
    """

    def __init__(self, allowed: dict[str, set[str]] | None = None) -> None:
        self._allowed: dict[str, set[str]] = allowed or {}

    def allow(self, channel: str, channel_user_id: str) -> None:
        self._allowed.setdefault(channel, set()).add(channel_user_id)

    def is_allowed(self, channel: str, channel_user_id: str) -> bool:
        if channel == "terminal":
            return True
        return channel_user_id in self._allowed.get(channel, set())
