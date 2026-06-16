"""Identity layer — loads the files that make Nexus "Nexus".

SOUL.md (global personality, slot #1), USER.md (your profile), TOOLS.md (tool
conventions). Pure natural language, provider-portable, so swapping models never
changes who Nexus is. The personality lives in *this* prompt assembly, not the
model.
"""

from nexus.identity.loader import Identity

__all__ = ["Identity"]
