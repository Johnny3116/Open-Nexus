"""SafetyPolicy — decide whether an action needs approval."""

from __future__ import annotations

from open_nexus.contracts.tool import ToolManifest
from open_nexus.safety.risk import is_irreversible


class SafetyPolicy:
    """Maps a tool manifest to a gate decision.

    A tool needs approval if it declares ``requires_approval`` OR its risk level
    is inherently irreversible/external. Default-deny on risk: a tool author who
    forgets the flag is still gated by their declared risk level.
    """

    def requires_approval(self, manifest: ToolManifest) -> bool:
        return manifest.requires_approval or is_irreversible(manifest.risk_level)
