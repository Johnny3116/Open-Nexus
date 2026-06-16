"""Skills — portable SKILL.md files (agentskills.io standard).

YAML frontmatter + natural-language instructions, loaded *on demand* by relevance
rather than all crammed into context. Phase 1 is human-authored only;
self-written procedural skills (the Hermes trick) are a Phase-4 luxury and a
security surface, so deferred.

SECURITY: treat every skill you didn't write as untrusted code. Fork, read,
install — no auto-install from a registry.
"""

from nexus.skills.loader import Skill, SkillLoader

__all__ = ["Skill", "SkillLoader"]
