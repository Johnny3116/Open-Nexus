"""Session resolution + per-session serialisation.

A session ties a user (resolved across channels — you-on-Telegram ==
you-on-terminal, full mapping arrives with the Supabase ``channel_identities``
table in Phase 2) to a channel and an ongoing conversation. A per-session lock
serialises concurrent messages so "a message arrives mid-run" is handled cleanly.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict

from pydantic import BaseModel


class Session(BaseModel):
    id: str
    user_id: str
    channel: str


class SessionRegistry:
    """In-memory session resolution + per-session locks (Phase 0).

    Phase 0 keys a session by ``(channel, channel_user_id)``. Phase 2 resolves a
    shared ``user_id`` across channels via the persisted identity map.
    """

    def __init__(self) -> None:
        self._sessions: dict[tuple[str, str], Session] = {}
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    def resolve(self, *, channel: str, channel_user_id: str) -> Session:
        key = (channel, channel_user_id)
        if key not in self._sessions:
            sid = f"{channel}:{channel_user_id}"
            self._sessions[key] = Session(id=sid, user_id=channel_user_id, channel=channel)
        return self._sessions[key]

    def lock_for(self, session_id: str) -> asyncio.Lock:
        return self._locks[session_id]
