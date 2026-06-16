"""VTube avatar control.

Drive a VTuber rig (VTube Studio's WebSocket API, or VSeeFace). Nexus emits small
declarative cues alongside text; this thin adapter maps cues -> rig. Keep the cue
vocabulary small and declarative (e.g. {"emotion": "amused", "gesture": "nod"})
so it stays model-portable.
"""

from __future__ import annotations


class VTubeAdapter:
    def __init__(self, *, ws_url: str) -> None:
        self.ws_url = ws_url

    async def apply(self, cues: dict) -> None:
        """Map a declarative cue dict onto the rig over the VTube Studio WS API."""
        # TODO(phase-3): connect to VTube Studio, translate {emotion, gesture}
        # cues into hotkey/parameter calls.
        raise NotImplementedError("VTubeAdapter.apply: Phase 3")
