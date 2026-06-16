"""Safety — risk policy and the approval gate, owned outside tools.

Tools declare risk (``ToolManifest.risk_level``); safety enforces it. The same
gate guards tools, skills, delegation, scheduler jobs, and remote control. This
is the non-negotiable layer given the eventual tool surface (remote control,
shell-capable skills, autonomous heartbeat).
"""

from open_nexus.safety.approval import ApprovalGate
from open_nexus.safety.policy import SafetyPolicy

__all__ = ["ApprovalGate", "SafetyPolicy"]
