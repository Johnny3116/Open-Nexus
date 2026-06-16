"""Safety policy: risk levels map to gate decisions."""

from __future__ import annotations

from open_nexus.contracts.tool import RiskLevel, ToolManifest
from open_nexus.safety.policy import SafetyPolicy


def test_read_is_never_gated():
    assert not SafetyPolicy().requires_approval(ToolManifest(name="r", risk_level=RiskLevel.READ))


def test_irreversible_levels_are_always_gated():
    policy = SafetyPolicy()
    for level in (RiskLevel.WRITE, RiskLevel.EXTERNAL, RiskLevel.SHELL, RiskLevel.CONTROL):
        # even with requires_approval False, the risk level forces the gate
        assert policy.requires_approval(ToolManifest(name="t", risk_level=level))
