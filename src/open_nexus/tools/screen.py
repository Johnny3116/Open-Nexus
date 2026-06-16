"""screen (Phase: senses) — capture → vision model. Opt-in per session, never silent."""

from __future__ import annotations

from open_nexus.contracts.tool import RiskLevel, ToolManifest

MANIFEST = ToolManifest(
    name="screen_capture",
    description="Capture the screen for a vision model. Explicit per-session opt-in.",
    risk_level=RiskLevel.EXTERNAL,
    requires_approval=True,
)


class ScreenCapture:
    def __init__(self) -> None:
        self._enabled_for_session = False

    def enable_for_session(self) -> None:
        self._enabled_for_session = True

    async def capture(self) -> bytes:
        if not self._enabled_for_session:
            raise PermissionError("screen capture not enabled for this session")
        raise NotImplementedError("screen: senses phase")
