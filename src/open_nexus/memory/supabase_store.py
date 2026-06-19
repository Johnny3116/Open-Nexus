"""SupabaseStore — the Phase-1+ persistent backend (Postgres + pgvector + FTS).

Implements the same ``MemoryStore`` protocol as ``SQLiteStore`` so the swap is a
config change, not a code change. The Supabase client is imported lazily and
requires the ``supabase`` extra.

SECURITY: this uses the service-role key, server-side only. No channel adapter,
widget, or web client ever touches Supabase directly — everything goes through
Core. See docs/nexus-build-plan.md §9 and memory/schema.sql (RLS).
"""

from __future__ import annotations

from open_nexus.contracts.message import Message, Role
from open_nexus.memory.base import StoredMessage


class SupabaseStore:
    def __init__(self, *, url: str, service_role_key: str) -> None:
        self._url = url
        self._service_role_key = service_role_key  # NEVER expose to a client
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from supabase import create_client  # lazy: requires the supabase extra

            self._client = create_client(self._url, self._service_role_key)
        return self._client

    def append_message(
        self, *, session_id: str, role: Role, content: str, tool_name: str | None = None
    ) -> StoredMessage:
        client = self._ensure_client()
        row = {
            "session_id": session_id,
            "role": role.value,
            "content": content,
            "tool_name": tool_name,
        }
        # id, created_at (and later the embedding) are filled by the DB.
        rows = client.table("messages").insert(row).execute().data
        if not rows:
            raise RuntimeError(
                "Supabase insert into messages returned no row "
                "(check RLS policy / table constraints)"
            )
        data = rows[0]
        return StoredMessage(
            id=str(data["id"]),
            session_id=session_id,
            role=Role(data["role"]),
            content=data["content"],
            tool_name=data.get("tool_name"),
            created_at=data["created_at"],
        )

    def recent(self, *, session_id: str, limit: int = 20) -> list[Message]:
        client = self._ensure_client()
        rows = (
            client.table("messages")
            .select("role,content,tool_name,created_at")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
            .data
        )
        # fetched newest-first; return oldest-first for prompt ordering.
        return [
            Message(role=Role(r["role"]), content=r["content"], tool_name=r.get("tool_name"))
            for r in reversed(rows)
        ]
        # TODO(persistent phase): layered retrieval (FTS + vector) via retrieval.py,
        # and FK-backed session/identity resolution (sessions + channel_identities).
