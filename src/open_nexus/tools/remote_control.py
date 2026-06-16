"""remote_control (Phase: senses) — keyboard/mouse/window automation.

The single most dangerous capability: RiskLevel.CONTROL, the hardest gate.
Suggest-and-confirm by default, never autonomous, scoped to one machine. Built
last. Stub until the senses phase.
"""

from __future__ import annotations

from open_nexus.contracts.tool import RiskLevel, ToolManifest

MANIFEST = ToolManifest(
    name="remote_control",
    description="Drive keyboard/mouse/windows on one scoped machine.",
    risk_level=RiskLevel.CONTROL,
    requires_approval=True,
)


async def handler(*, action: str, **kwargs) -> dict:
    raise NotImplementedError("remote_control: senses phase (hardest gate)")
