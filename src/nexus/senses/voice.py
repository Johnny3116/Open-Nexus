"""Voice box — STT in, TTS out, wired as a channel-level transform.

Wiring it as a transform (rather than a one-off channel) means *any* channel can
be voice-enabled. STT: Whisper local or a hosted API. Requires the `voice` extra.
"""

from __future__ import annotations


class VoiceTransform:
    """Wraps a channel: audio in -> STT -> text; text out -> TTS -> audio."""

    def __init__(self, *, stt_backend: str = "local", tts_backend: str = "local") -> None:
        self.stt_backend = stt_backend
        self.tts_backend = tts_backend

    async def transcribe(self, audio: bytes) -> str:
        raise NotImplementedError("VoiceTransform.transcribe: Phase 3")

    async def synthesize(self, text: str) -> bytes:
        raise NotImplementedError("VoiceTransform.synthesize: Phase 3")
