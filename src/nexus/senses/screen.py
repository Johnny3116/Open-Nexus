"""Screen capture / vision.

Periodic or on-demand screenshots fed to a vision-capable model so Nexus can
"see" what you're looking at. PRIVACY GATE: explicit opt-in per session, never
silent. Requires the `vision` extra.
"""

from __future__ import annotations


class ScreenCapture:
    def __init__(self) -> None:
        # Off until explicitly enabled for the current session.
        self._enabled_for_session = False

    def enable_for_session(self) -> None:
        """Explicit per-session opt-in. Capture is impossible until this is set."""
        self._enabled_for_session = True

    async def capture(self) -> bytes:
        if not self._enabled_for_session:
            raise PermissionError("screen capture not enabled for this session")
        # TODO(phase-3): grab a screenshot (mss) and return PNG bytes.
        raise NotImplementedError("ScreenCapture.capture: Phase 3")
