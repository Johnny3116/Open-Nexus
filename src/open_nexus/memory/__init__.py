"""Memory — an interface with swappable backends.

Phase 0 uses ``SQLiteStore`` (stdlib, zero setup) so the harness runs immediately
— no Docker, no Supabase CLI, no pgvector, no migrations. ``SupabaseStore`` lands
in a later phase for the deployed, persistent Nexus. Both satisfy ``MemoryStore``.
"""

from open_nexus.memory.base import MemoryStore, StoredMessage
from open_nexus.memory.sqlite_store import SQLiteStore

__all__ = ["MemoryStore", "StoredMessage", "SQLiteStore"]
