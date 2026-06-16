"""MemoryStore protocol — the contract every backend implements."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from open_nexus.contracts.message import Message, Role


class StoredMessage(BaseModel):
    """A persisted turn, with its id and ordering timestamp."""

    id: str
    session_id: str
    role: Role
    content: str
    tool_name: str | None = None
    created_at: str  # ISO 8601


@runtime_checkable
class MemoryStore(Protocol):
    """Persist and recall conversation turns. Backend-agnostic."""

    def append_message(
        self, *, session_id: str, role: Role, content: str, tool_name: str | None = None
    ) -> StoredMessage:
        """Persist one turn and return it."""
        ...

    def recent(self, *, session_id: str, limit: int = 20) -> list[Message]:
        """Return the most recent turns for a session, oldest-first."""
        ...
