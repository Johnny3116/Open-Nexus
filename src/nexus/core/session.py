"""Session resolution and lifecycle.

A session ties a user (resolved across channel identities — you on Telegram is
the same user as you on Discord) to a channel and an ongoing conversation. Maps
to the ``sessions`` table.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Session:
    """An in-memory handle on a conversation. Persisted to the `sessions` table."""

    id: str
    user_id: str
    channel: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        self.last_active = datetime.now(timezone.utc)


# TODO(phase-0): resolve_session(channel, channel_user_id) — look up / create the
# user via channel_identities, enforce the per-channel allowlist, open or resume
# a session row.
