"""Build the memory backend from config.

`sqlite` (Phase 0, zero setup) or `supabase` (persistent). Both satisfy the
``MemoryStore`` protocol, so the rest of the harness is unaffected by the choice.
The Supabase client is imported lazily inside its branch.
"""

from __future__ import annotations

from open_nexus.config import Config
from open_nexus.memory.base import MemoryStore
from open_nexus.memory.sqlite_store import SQLiteStore


def build_store(cfg: Config) -> MemoryStore:
    backend = cfg.memory.backend
    if backend == "sqlite":
        return SQLiteStore(cfg.memory.path)
    if backend == "supabase":
        from open_nexus.memory.supabase_store import SupabaseStore

        if not (cfg.secrets.supabase_url and cfg.secrets.supabase_service_role_key):
            raise ValueError("supabase backend needs SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY")
        return SupabaseStore(
            url=cfg.secrets.supabase_url,
            service_role_key=cfg.secrets.supabase_service_role_key,
        )
    raise ValueError(f"unknown memory backend: {backend!r}")
