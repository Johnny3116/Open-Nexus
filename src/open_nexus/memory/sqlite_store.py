"""SQLiteStore — the Phase-0 memory backend. Stdlib only, zero setup.

Gets the harness working immediately. Use ``:memory:`` in unit tests and a file
path in real runs. The deployed Nexus swaps in ``SupabaseStore`` later without the
core loop noticing.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import UTC, datetime

from open_nexus.contracts.message import Message, Role
from open_nexus.memory.base import StoredMessage

_SCHEMA = """
create table if not exists messages (
    id          text primary key,
    session_id  text not null,
    role        text not null,
    content     text not null,
    tool_name   text,
    created_at  text not null
);
create index if not exists messages_session_idx on messages (session_id, created_at);
"""


class SQLiteStore:
    """A minimal message store backed by SQLite."""

    def __init__(self, path: str = ":memory:") -> None:
        # check_same_thread=False keeps it usable from the async loop's executor.
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def append_message(
        self, *, session_id: str, role: Role, content: str, tool_name: str | None = None
    ) -> StoredMessage:
        msg = StoredMessage(
            id=uuid.uuid4().hex,
            session_id=session_id,
            role=role,
            content=content,
            tool_name=tool_name,
            created_at=datetime.now(UTC).isoformat(),
        )
        self._conn.execute(
            "insert into messages (id, session_id, role, content, tool_name, created_at)"
            " values (?, ?, ?, ?, ?, ?)",
            (msg.id, msg.session_id, msg.role.value, msg.content, msg.tool_name, msg.created_at),
        )
        self._conn.commit()
        return msg

    def recent(self, *, session_id: str, limit: int = 20) -> list[Message]:
        rows = self._conn.execute(
            "select role, content, tool_name from messages"
            " where session_id = ? order by created_at desc limit ?",
            (session_id, limit),
        ).fetchall()
        # fetched newest-first; return oldest-first for prompt ordering.
        return [
            Message(role=Role(r["role"]), content=r["content"], tool_name=r["tool_name"])
            for r in reversed(rows)
        ]

    def close(self) -> None:
        self._conn.close()
