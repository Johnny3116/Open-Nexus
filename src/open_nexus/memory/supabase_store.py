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
        # TODO(phase-1): insert into `messages`, populate embedding async.
        raise NotImplementedError("SupabaseStore.append_message: Phase 1")

    def recent(self, *, session_id: str, limit: int = 20) -> list[Message]:
        # TODO(phase-1): select recent rows for the session.
        raise NotImplementedError("SupabaseStore.recent: Phase 1")
