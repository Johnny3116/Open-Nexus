"""Skills — portable capabilities loaded on demand.

Each skill is a directory with a machine-readable ``skill.toml`` (id, version,
entrypoint, permissions) and a model-readable ``SKILL.md`` (natural-language
instructions). Machines read the manifest; humans and LLMs read the Markdown —
don't make Markdown the only source of truth.

SECURITY: treat any skill you didn't write as untrusted. Fork, read, install —
no auto-install from a registry. Self-written skills (Phase 4) need human
approval before activation.
"""

from open_nexus.skills.loader import Skill, SkillLoader

__all__ = ["Skill", "SkillLoader"]
