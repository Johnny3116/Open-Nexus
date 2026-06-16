"""voice (Phase: senses) — STT in / TTS out, wired as a channel-level transform.

Wiring it as a transform means any channel can be voice-enabled, rather than
voice being a one-off channel. Stub until the senses phase.
"""

from __future__ import annotations


class VoiceTransform:
    async def transcribe(self, audio: bytes) -> str:
        raise NotImplementedError("voice: senses phase")

    async def synthesize(self, text: str) -> bytes:
        raise NotImplementedError("voice: senses phase")
