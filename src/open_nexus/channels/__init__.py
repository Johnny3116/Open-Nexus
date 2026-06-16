"""Channels — dumb adapters per surface.

A channel only normalises inbound payloads and serialises outbound replies. Auth,
allowlists, session resolution, and the agent loop all live in the gateway/core.
Core never imports a channel; the gateway wires them together. Slack is
intentionally omitted (add later only with a real reason).
"""

from open_nexus.channels.terminal import TerminalChannel

__all__ = ["TerminalChannel"]
