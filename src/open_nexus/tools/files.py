"""files — triage / rename / organise (write risk; deletes gated). Later phase."""

from __future__ import annotations

from open_nexus.contracts.tool import RiskLevel, ToolManifest

MANIFEST = ToolManifest(
    name="files",
    description="Sort, rename, and organise files in a target directory.",
    risk_level=RiskLevel.WRITE,  # mutates the filesystem → gated by default
    requires_approval=True,
)


async def handler(*, action: str, path: str) -> dict:
    raise NotImplementedError("files: later phase")
