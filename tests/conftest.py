"""Shared fixtures.

The load-bearing one is the provider seam: tests inject ``EchoProvider`` or
``FakeProvider`` (from ``open_nexus.providers.fake``) so the loop runs
deterministically with no network and no cost.
"""

from __future__ import annotations

import pytest

from open_nexus.core.context import ContextAssembler
from open_nexus.memory.sqlite_store import SQLiteStore
from open_nexus.runtime.state import RuntimeState


@pytest.fixture
def store() -> SQLiteStore:
    return SQLiteStore(":memory:")


@pytest.fixture
def assembler(tmp_path) -> ContextAssembler:
    # Minimal identity so the system prompt is deterministic and self-contained.
    (tmp_path / "SOUL.md").write_text("You are Nexus.", encoding="utf-8")
    return ContextAssembler(identity_dir=tmp_path)


@pytest.fixture
def state() -> RuntimeState:
    return RuntimeState(
        session_id="terminal:local",
        user_id="local",
        active_model="fake",
        active_channel="terminal",
    )
