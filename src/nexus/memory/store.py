"""MemoryStore — the write/read gateway to Supabase.

Owns the service-role connection (server-side only). Everything that persists a
turn or loads core memory goes through here.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CoreMemory:
    """Layer-1 payload: curated facts/preferences + the user profile JSON."""

    entries: list[dict]
    profile: dict


class MemoryStore:
    def __init__(self, *, url: str, service_role_key: str, database_url: str) -> None:
        self._url = url
        self._service_role_key = service_role_key  # NEVER expose to a client
        self._database_url = database_url
        # TODO(phase-0): create the supabase/psycopg client(s).

    # --- writes ---
    def append_message(self, *, session_id: str, role: str, content: str, tool_name=None) -> None:
        """Persist one turn to Layer 2 (`messages`). Embeddings filled async."""
        raise NotImplementedError("MemoryStore.append_message: Phase 0")

    def write_core(self, *, user_id: str, kind: str, content: str, priority: int = 0) -> None:
        """Write a durable fact/preference/note to Layer 1 (`nexus_memory`)."""
        raise NotImplementedError("MemoryStore.write_core: Phase 1")

    # --- reads ---
    def core(self, user_id: str, *, cap: int = 1500) -> CoreMemory:
        """Load Layer-1 core memory, capped to ~cap tokens to force prioritisation."""
        raise NotImplementedError("MemoryStore.core: Phase 1")
