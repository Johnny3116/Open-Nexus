"""Tools — capabilities the model can call, each gated by ``safety``.

A tool pairs a ``ToolManifest`` (what it is + how risky) with an async handler.
The registry runs every call through the ``ApprovalGate``, so nothing with side
effects fires without passing the gate. Phase-3 sense tools (voice/screen/
remote_control/vtube) are stubs here so the shape is visible early.
"""

from open_nexus.tools.base import Tool
from open_nexus.tools.registry import ToolRegistry

__all__ = ["Tool", "ToolRegistry"]
