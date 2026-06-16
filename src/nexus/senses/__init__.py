"""Senses — Nexus's differentiating special tools (Phase 3).

Each goes through the approval gate. Build order within the phase: voice (as a
channel transform) -> desktop widget -> screen vision -> remote control (last,
behind the hardest gates) -> VTube avatar.

    voice          TTS out / STT in, wired as a channel-level transform so *any*
                   channel can be voice-enabled.
    screen         periodic/on-demand screenshots to a vision model. Explicit
                   opt-in per session, never silent.
    remote_control keyboard/mouse/window automation. The single most dangerous
                   capability. Suggest-and-confirm only; never autonomous.
    desktop_widget small always-on-top window over the web-UI WebSocket.
    vtube          drive a VTuber rig via small declarative {emotion, gesture} cues.
"""
