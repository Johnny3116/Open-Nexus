"""SQLiteStore: append + recent ordering."""

from __future__ import annotations

from open_nexus.contracts.message import Role
from open_nexus.memory.sqlite_store import SQLiteStore


def test_append_and_recent_oldest_first():
    s = SQLiteStore(":memory:")
    for i in range(3):
        s.append_message(session_id="sess", role=Role.USER, content=f"m{i}")
    history = s.recent(session_id="sess", limit=2)
    # recent(limit=2) returns the last two, oldest-first
    assert [m.content for m in history] == ["m1", "m2"]


def test_sessions_are_isolated():
    s = SQLiteStore(":memory:")
    s.append_message(session_id="a", role=Role.USER, content="hi a")
    s.append_message(session_id="b", role=Role.USER, content="hi b")
    assert [m.content for m in s.recent(session_id="a")] == ["hi a"]
