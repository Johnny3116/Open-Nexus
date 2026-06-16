"""Risk classification helpers.

Centralises which ``RiskLevel``s are considered irreversible/external and thus
gate-by-default, independent of any individual tool's ``requires_approval`` flag.
"""

from __future__ import annotations

from open_nexus.contracts.tool import RiskLevel

# Anything at or above these always requires explicit human approval, regardless
# of the tool's own flag. READ never does.
ALWAYS_GATED: frozenset[RiskLevel] = frozenset(
    {RiskLevel.WRITE, RiskLevel.EXTERNAL, RiskLevel.SHELL, RiskLevel.CONTROL}
)


def is_irreversible(level: RiskLevel) -> bool:
    return level in ALWAYS_GATED
