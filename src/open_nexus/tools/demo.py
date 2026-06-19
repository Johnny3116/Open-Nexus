"""Demo tools for Phase 3 — one read-only, one gated.

- ``clock`` (RiskLevel.READ): no side effects, runs without approval.
- ``write_note`` (RiskLevel.WRITE): mutates state, so it is blocked until the
  approval gate gets a yes. It writes to an in-process dict (not the real
  filesystem) so tests stay hermetic while still demonstrating a gated write.

These exist to prove the safety wiring end to end; real tools (files, research,
the senses) build on the same ``Tool`` + ``ToolManifest`` shape.
"""

from __future__ import annotations

from datetime import UTC, datetime

from open_nexus.contracts.tool import RiskLevel, ToolManifest
from open_nexus.tools.base import Tool


def clock_tool() -> Tool:
    async def handler() -> dict[str, str]:
        return {"utc": datetime.now(UTC).isoformat()}

    return Tool(
        manifest=ToolManifest(
            name="clock",
            description="Return the current UTC time.",
            risk_level=RiskLevel.READ,
        ),
        handler=handler,
    )


def write_note_tool(store: dict[str, str] | None = None) -> Tool:
    """A gated write tool. ``store`` is an in-process dict standing in for a
    side-effecting sink; defaults to a fresh dict held by the closure."""
    notes: dict[str, str] = store if store is not None else {}

    async def handler(*, key: str, value: str) -> dict[str, str]:
        notes[key] = value
        return {"written": key}

    tool = Tool(
        manifest=ToolManifest(
            name="write_note",
            description="Store a note. Mutates state, so it is gated.",
            risk_level=RiskLevel.WRITE,
            requires_approval=True,
            parameters={"key": "str", "value": "str"},
        ),
        handler=handler,
    )
    # Expose the sink for assertions in tests.
    tool.notes = notes  # type: ignore[attr-defined]
    return tool
