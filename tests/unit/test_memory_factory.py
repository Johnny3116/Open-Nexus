"""Memory backend selection from config."""

from __future__ import annotations

import pytest

from open_nexus.config import Config, MemoryConfig, ProvidersConfig, Secrets
from open_nexus.memory.factory import build_store
from open_nexus.memory.sqlite_store import SQLiteStore


def _cfg(memory: MemoryConfig) -> Config:
    # Explicit None secrets so the test is deterministic regardless of host env.
    secrets = Secrets(supabase_url=None, supabase_service_role_key=None)
    return Config(secrets=secrets, routing=ProvidersConfig(), memory=memory)


def test_default_backend_is_sqlite():
    store = build_store(_cfg(MemoryConfig(backend="sqlite", path=":memory:")))
    assert isinstance(store, SQLiteStore)


def test_supabase_backend_requires_credentials():
    # No SUPABASE_URL/key in Secrets → fail fast with a clear error.
    with pytest.raises(ValueError, match="supabase backend needs"):
        build_store(_cfg(MemoryConfig(backend="supabase")))


def test_unknown_backend_rejected():
    with pytest.raises(ValueError, match="unknown memory backend"):
        build_store(_cfg(MemoryConfig(backend="redis")))
