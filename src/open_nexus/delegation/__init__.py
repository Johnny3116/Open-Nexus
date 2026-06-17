"""Delegation — Nexus hands coding off to Jarvis.

Coding is deliberately carved out of Nexus, so it is a first-class capability, not
a gap. When a conversation turns into "build/fix/refactor," Nexus composes a
``TaskPacket`` (with verification steps), hands it to Jarvis, and reports back in
its own voice. The handoff *fails closed*: if Jarvis isn't configured, delegation
raises rather than silently pretending the work was sent.
"""

from open_nexus.delegation.jarvis import DelegationNotConfigured, JarvisDelegate

__all__ = ["JarvisDelegate", "DelegationNotConfigured"]
