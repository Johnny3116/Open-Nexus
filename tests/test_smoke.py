"""Smoke tests for the Phase-0 scaffold.

These assert the package imports cleanly and the structural pieces exist. They do
*not* test runtime behaviour (most of which is NotImplementedError until its
phase lands).
"""

from pathlib import Path

import nexus


def test_version() -> None:
    assert nexus.__version__


def test_core_imports() -> None:
    from nexus.channels.base import Channel
    from nexus.core import loop  # noqa: F401
    from nexus.identity import Identity
    from nexus.providers.base import Provider
    from nexus.tools import ApprovalGate, ToolRegistry  # noqa: F401

    assert Channel and Provider and Identity


def test_identity_files_present() -> None:
    identity_dir = Path(__file__).resolve().parents[1] / "identity"
    for name in ("SOUL.md", "USER.md", "TOOLS.md", "HEARTBEAT.md"):
        assert (identity_dir / name).exists(), f"missing identity/{name}"


def test_identity_loader_reads_soul() -> None:
    from nexus.identity import Identity

    root = Path(__file__).resolve().parents[1]
    identity = Identity(identity_dir=root / "identity")
    assert "Nexus" in identity.soul()


def test_schema_and_skills_present() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "db" / "schema.sql").exists()
    assert list((root / "skills").glob("*/SKILL.md")), "no SKILL.md files found"
