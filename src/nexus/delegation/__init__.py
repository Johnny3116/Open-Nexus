"""Delegation — Nexus hands coding off to Jarvis.

Coding is deliberately carved out of Nexus's job, so it's a first-class tool, not
a gap. When a conversation turns into "build / fix / refactor," Nexus hands a
well-formed task to Jarvis, monitors it, and reports back in its own voice. Two
specialists, one front door — keeps Nexus light and more useful than a monolith.
"""

from nexus.delegation.jarvis import JarvisDelegate

__all__ = ["JarvisDelegate"]
