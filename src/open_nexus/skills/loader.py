"""Skill discovery + loading from ``skill.toml`` + ``SKILL.md``."""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field


class SkillPermissions(BaseModel):
    network: bool = False
    filesystem: bool = False
    shell: bool = False
    requires_approval: bool = True  # untrusted-by-default


class Skill(BaseModel):
    id: str
    name: str
    version: str = "0.0.0"
    entrypoint: str | None = None
    permissions: SkillPermissions = Field(default_factory=SkillPermissions)
    instructions: str = ""  # the SKILL.md body
    path: Path

    model_config = {"arbitrary_types_allowed": True}


class SkillLoader:
    def __init__(self, skills_dir: str | Path = "skills") -> None:
        self.dir = Path(skills_dir)

    def discover(self) -> list[Path]:
        """Skill dirs are those containing a machine-readable manifest."""
        return sorted(p.parent for p in self.dir.glob("*/skill.toml"))

    def load(self, skill_dir: Path) -> Skill:
        manifest = tomllib.loads((skill_dir / "skill.toml").read_text(encoding="utf-8"))
        md = skill_dir / "SKILL.md"
        perms = SkillPermissions.model_validate(manifest.get("permissions", {}))
        return Skill(
            id=manifest["id"],
            name=manifest.get("name", manifest["id"]),
            version=manifest.get("version", "0.0.0"),
            entrypoint=manifest.get("entrypoint"),
            permissions=perms,
            instructions=md.read_text(encoding="utf-8") if md.exists() else "",
            path=skill_dir,
        )

    def relevant(self, query: str) -> list[Skill]:
        # TODO(phase: skills): match triggers/description against the query.
        raise NotImplementedError("SkillLoader.relevant: skills phase")
