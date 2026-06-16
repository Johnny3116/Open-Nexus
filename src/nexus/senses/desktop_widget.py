"""Desktop widget — a small always-on-top window.

Talks to Core over the same WebSocket the web UI uses (so it's just another web
client, never touching Supabase or providers directly). Shows current state, the
last message, a push-to-talk button, and quick actions. The UI itself (Tauri /
Electron / PyQt-QML) lives outside this package; this module is the Core-side
contract it connects to.
"""

from __future__ import annotations

# TODO(phase-3): define the widget <-> Core WebSocket message contract
# (state updates, last-message, push-to-talk audio frames, quick-action calls).
