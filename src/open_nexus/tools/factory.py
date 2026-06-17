"""Build the tool registry + approval wiring.

The registry's gate uses the ``ApprovalManager`` as its confirmer, so a gated
tool suspends on the manager's pending queue until the API (or another surface)
approves or rejects it. Phase 3 registers the demo tools; later phases add the
real ones (files, research, the senses) the same way.
"""

from __future__ import annotations

from open_nexus.safety.approval import ApprovalGate
from open_nexus.safety.approval_manager import ApprovalManager
from open_nexus.tools.demo import clock_tool, write_note_tool
from open_nexus.tools.registry import ToolRegistry


def build_tools(manager: ApprovalManager) -> ToolRegistry:
    gate = ApprovalGate(confirmer=manager.confirm)
    registry = ToolRegistry(gate=gate)
    registry.register(clock_tool())
    registry.register(write_note_tool())
    return registry
