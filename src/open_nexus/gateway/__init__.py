"""Gateway — the control plane between channels and the core (OpenClaw-style).

Owns the pipeline:

    channel input → auth / allowlist → normalize → session resolution
                  → build RuntimeState → hand off to core loop → serialize out

Channels are dumb adapters; the core knows no channel. The gateway is the only
thing that knows both.
"""

from open_nexus.gateway.auth import Allowlist
from open_nexus.gateway.router import Gateway

__all__ = ["Gateway", "Allowlist"]
