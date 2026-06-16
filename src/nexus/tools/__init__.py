"""Tool runtime + the approval gate.

Every irreversible or external action (remote-control clicks/keystrokes, file
deletes, sending messages/emails, anything that spends money) passes through the
approval gate before it runs. This is Hermes' dangerous-command approval layer,
ported. Default to suggest-and-confirm.
"""

from nexus.tools.approval import ApprovalGate, ApprovalRequest
from nexus.tools.registry import Tool, ToolRegistry
from nexus.tools.runtime import ToolRuntime

__all__ = ["Tool", "ToolRegistry", "ApprovalGate", "ApprovalRequest", "ToolRuntime"]
