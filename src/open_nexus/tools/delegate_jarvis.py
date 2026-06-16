"""delegate_to_jarvis — hand coding tasks to the delegated coding agent.

Coding is deliberately carved out of Nexus. When a conversation turns into
"build/fix/refactor," Nexus composes a ``TaskPacket``, hands it to Jarvis (Claude
Code), monitors it, and reports back in its own voice. Two specialists, one front
door. Implemented in the delegation phase; the contract is in ``contracts.task``.
"""

from __future__ import annotations

from open_nexus.contracts.task import TaskPacket


async def delegate(packet: TaskPacket) -> TaskPacket:
    # TODO(phase: skills): submit to the Jarvis endpoint, poll/stream status,
    # return the updated packet.
    raise NotImplementedError("delegate_to_jarvis: later phase")
