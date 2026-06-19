"""Skill loading, relevance/activation, fail-closed, and the human-only guardrail."""

from __future__ import annotations

from pathlib import Path

from open_nexus.skills.loader import HUMAN_AUTHORED_ONLY, SkillLoader

REPO_SKILLS = Path(__file__).resolve().parents[2] / "skills"


def _loader(tmp_path) -> SkillLoader:
    return SkillLoader(skills_dir=tmp_path)


def _write_skill(root: Path, sid: str, *, keywords: list[str], toml_extra: str = "") -> None:
    d = root / sid
    d.mkdir(parents=True)
    kw = ", ".join(f'"{k}"' for k in keywords)
    (d / "skill.toml").write_text(
        f'id = "{sid}"\nname = "{sid}"\nkeywords = [{kw}]\n{toml_extra}', encoding="utf-8"
    )
    (d / "SKILL.md").write_text(f"# {sid}\ninstructions", encoding="utf-8")


# --- discovery + parsing (against the real repo skills) ---------------------


def test_discovers_repo_skills():
    loader = SkillLoader(skills_dir=REPO_SKILLS)
    ids = {s.id for s in loader.load_all()}
    assert {"research-and-summarise", "file-triage", "daily-briefing"} <= ids


def test_parses_keywords_and_permissions():
    loader = SkillLoader(skills_dir=REPO_SKILLS)
    triage = next(s for s in loader.load_all() if s.id == "file-triage")
    assert "rename" in triage.keywords
    assert triage.permissions.requires_approval is True  # untrusted-by-default


# --- relevance / activation -------------------------------------------------


def test_relevant_ranks_by_keyword_hits(tmp_path):
    _write_skill(tmp_path, "research-and-summarise", keywords=["research", "latest"])
    _write_skill(tmp_path, "file-triage", keywords=["file", "sort"])
    loader = _loader(tmp_path)
    hits = loader.relevant("please research the latest news")
    assert hits and hits[0].id == "research-and-summarise"


def test_irrelevant_query_activates_nothing(tmp_path):
    _write_skill(tmp_path, "file-triage", keywords=["file", "sort"])
    assert _loader(tmp_path).relevant("what's the weather") == []


def test_relevance_respects_top_k(tmp_path):
    for i in range(5):
        _write_skill(tmp_path, f"s{i}", keywords=["go"])
    assert len(_loader(tmp_path).relevant("go go go", top_k=2)) == 2


# --- fail-closed + guardrail ------------------------------------------------


def test_malformed_skill_is_skipped_not_fatal(tmp_path):
    _write_skill(tmp_path, "good", keywords=["ok"])
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "skill.toml").write_text("this is not = valid = toml", encoding="utf-8")
    ids = {s.id for s in _loader(tmp_path).load_all()}
    assert ids == {"good"}  # bad one skipped, discovery survives


def test_load_does_not_import_entrypoint(tmp_path):
    # A bogus entrypoint must not be imported/executed — loading only records it.
    _write_skill(tmp_path, "x", keywords=["k"], toml_extra='entrypoint = "does.not.exist"\n')
    skill = _loader(tmp_path).load_all()[0]
    assert skill.entrypoint == "does.not.exist"  # recorded as text, never imported


def test_guardrail_human_authored_only():
    # No skill-creation/writing API exists on the loader (Phase 4 is read-only).
    assert HUMAN_AUTHORED_ONLY is True
    assert not any(hasattr(SkillLoader, m) for m in ("create", "write", "author", "generate"))


def test_load_all_is_cached_until_reload(tmp_path):
    import shutil

    _write_skill(tmp_path, "good", keywords=["ok"])
    loader = _loader(tmp_path)
    first = loader.load_all()
    assert [s.id for s in first] == ["good"]

    shutil.rmtree(tmp_path / "good")  # remove from disk
    assert [s.id for s in loader.load_all()] == ["good"]  # served from cache, no re-read

    loader.reload()
    assert loader.load_all() == []  # cache dropped → re-reads (now empty)
