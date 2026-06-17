"""Skill discovery, loading, and relevance — human-authored skills only.

A skill is a directory under the skills dir with a machine-readable ``skill.toml``
(id, version, keywords, permissions) and a model-readable ``SKILL.md`` (the
instructions). Machines read the manifest; humans/LLMs read the Markdown.

GUARDRAIL (Phase 4): this loader is **read-only** and loads **only human-authored
skills from the configured skills directory**. There is no skill-creation/writing
API, and ``load`` never imports or executes a skill's ``entrypoint`` — it only
records it as a string. Self-authored skills (Nexus proposing its own skills) are
a later phase and will require explicit human approval before activation.

Loading is **fail-closed**: a malformed or unreadable skill is skipped (logged),
never crashing discovery, and skills default to untrusted (``requires_approval``).
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

from open_nexus.observability.logger import get_logger

_log = get_logger("open_nexus.skills")

# Phase 4 loads only human-authored skills. Flip nothing here to "enable"
# self-authoring — that is a separate, approval-gated phase.
HUMAN_AUTHORED_ONLY = True


class SkillPermissions(BaseModel):
    network: bool = False
    filesystem: bool = False
    shell: bool = False
    requires_approval: bool = True  # untrusted-by-default


class Skill(BaseModel):
    id: str
    name: str
    version: str = "0.0.0"
    entrypoint: str | None = None  # recorded only; never imported/executed here
    keywords: list[str] = Field(default_factory=list)
    description: str = ""
    permissions: SkillPermissions = Field(default_factory=SkillPermissions)
    instructions: str = ""  # the SKILL.md body
    path: Path

    model_config = {"arbitrary_types_allowed": True}

    def score(self, query: str) -> int:
        """Relevance of this skill to a query: keyword/name substring hits."""
        q = query.lower()
        hits = sum(1 for kw in self.keywords if kw.lower() in q)
        if self.name.lower() in q:
            hits += 1
        return hits


class SkillLoader:
    def __init__(self, skills_dir: str | Path = "skills") -> None:
        self.dir = Path(skills_dir)

    def discover(self) -> list[Path]:
        """Skill dirs are those containing a machine-readable manifest."""
        return sorted(p.parent for p in self.dir.glob("*/skill.toml"))

    def load(self, skill_dir: Path) -> Skill:
        """Parse one skill. Records ``entrypoint`` as text — never imports it."""
        manifest = tomllib.loads((skill_dir / "skill.toml").read_text(encoding="utf-8"))
        md = skill_dir / "SKILL.md"
        perms = SkillPermissions.model_validate(manifest.get("permissions", {}))
        return Skill(
            id=manifest["id"],
            name=manifest.get("name", manifest["id"]),
            version=manifest.get("version", "0.0.0"),
            entrypoint=manifest.get("entrypoint"),
            keywords=list(manifest.get("keywords", [])),
            description=manifest.get("description", ""),
            permissions=perms,
            instructions=md.read_text(encoding="utf-8") if md.exists() else "",
            path=skill_dir,
        )

    def load_all(self) -> list[Skill]:
        """Load every discoverable skill, skipping any that fail to parse."""
        skills: list[Skill] = []
        for skill_dir in self.discover():
            try:
                skills.append(self.load(skill_dir))
            except Exception as exc:  # noqa: BLE001 - fail closed: skip, don't crash
                _log.warning("skipping unloadable skill at %s: %s", skill_dir, exc)
        return skills

    def relevant(self, query: str, *, top_k: int = 3) -> list[Skill]:
        """Return up to ``top_k`` skills relevant to the query, best first.

        Activation is on-demand by relevance — skills are not all crammed into
        context. A skill with zero keyword/name hits is not activated.
        """
        scored = [(s.score(query), s) for s in self.load_all()]
        ranked = sorted(
            (pair for pair in scored if pair[0] > 0),
            key=lambda pair: (-pair[0], pair[1].id),
        )
        return [s for _, s in ranked[:top_k]]
