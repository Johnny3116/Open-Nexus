"""Integration: SupabaseStore against a real Postgres (Phase 1).

Marked ``integration`` so it only runs when local Supabase/Postgres is up and the
env is configured. Skipped otherwise — CI runs unit tests only until the memory
phase adds the Postgres service container.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skipif(not os.getenv("SUPABASE_URL"), reason="needs local Supabase")
def test_supabase_roundtrip():
    # TODO(phase: persistent): append + recent against a real schema-applied DB.
    pytest.skip("SupabaseStore not implemented until the persistent-nexus phase")
