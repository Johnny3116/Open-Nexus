"""research — fan-out search + summarise (read-only). Later phase."""

from __future__ import annotations

from open_nexus.contracts.tool import RiskLevel, ToolManifest

MANIFEST = ToolManifest(
    name="research",
    description="Research a topic across sources and return a cited summary.",
    risk_level=RiskLevel.EXTERNAL,  # makes outbound network calls
    requires_approval=False,
)


async def handler(*, query: str) -> dict:
    raise NotImplementedError("research: later phase")
