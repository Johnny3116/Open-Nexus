"""vtube (Phase: senses) — declarative {emotion, gesture} cues → VTube Studio WS.

Keep the cue vocabulary small and declarative so it stays model-portable. Stub
until the senses phase.
"""

from __future__ import annotations


class VTubeAdapter:
    def __init__(self, *, ws_url: str) -> None:
        self.ws_url = ws_url

    async def apply(self, cues: dict) -> None:
        raise NotImplementedError("vtube: senses phase")
