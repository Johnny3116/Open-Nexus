"""Runtime state — the object threaded through the harness.

``RuntimeState`` is passed through the gateway → core loop → tools/safety so no
subsystem has to smuggle state through globals or config. (Without it, every
subsystem eventually grows a back-channel — classic haunted-house behaviour.)
"""

from open_nexus.runtime.state import RuntimeState

__all__ = ["RuntimeState"]
