# Open-Nexus — Project Build Plan

*How we set up the repo, build it, test it, change it, and ship it. Companion to
`nexus-harness-design.md` — that doc is **what** we build; this is **how**.*

## 0. The loop

```
issue → branch → build → test (local) → PR → CI green → review → merge → delete branch
```

- **Issues are the unit of work.** Each maps to one item in a phase milestone.
- **Jarvis writes the code; you review and steer.**
- **`main` is always green and deployable.** Protected; nothing lands except via a
  passing PR.
- **Small PRs.** One issue, one concern, one PR.

## 1. Tech stack (locked)

| Layer | Choice |
|---|---|
| Language | Python 3.13 (pinned in `.python-version`) |
| Package/env | uv |
| Lint + format | Ruff |
| Types | mypy |
| Tests | pytest + pytest-asyncio |
| Config | pydantic v2 + pydantic-settings (secrets) + YAML (provider routing) |
| Async HTTP | httpx |
| DB | SQLite (Phase 0) → Supabase / Postgres + pgvector (persistent phase) |
| Secret scanning | gitleaks (pre-commit + CI) |
| CI | GitHub Actions |

Versions are resolved by `uv.lock`, not hand-pinned here.

## 2. Repository structure

See the tree in the repo root. Module boundaries mirror the architecture:
`contracts/` (owned by the harness), `gateway/` (auth + normalise + session),
`core/` (loop/session/context), `providers/` (router + adapters), `channels/`
(dumb adapters), `memory/` (interface + sqlite/supabase), `safety/` (policy +
gate), `observability/`, `tools/`, `skills/`, `scheduler/`, `api/`.

## 4. Local dev

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # install uv
uv sync                                            # build env from the lockfile
uv run pre-commit install                          # secret-scan + lint hooks
uv run open-nexus chat                             # Phase 0: echo provider, SQLite
```

Phase 0 needs no keys, no Docker, no Supabase. Point `config.yaml` at a real
provider and set keys in `.env` when ready.

## 5. Testing strategy

The agent is non-deterministic and costs money, so the seam is the **provider
boundary**: the loop talks to the `Provider` protocol and tests inject
`FakeProvider`/`EchoProvider`. Three tiers:

- **Unit** (no I/O): contracts, context assembly, router fallback, the safety
  gate, gateway auth, SQLite store. The bulk of the suite; milliseconds.
- **Integration** (`-m integration`): the loop against local Supabase/Postgres.
  Gated behind Docker.
- **Live** (`-m live`): a tiny real-provider smoke, manual, never in CI.

Rules: every bug fix starts with a failing test; every side-effecting tool gets a
test that it's gated; `uv run pytest` before every PR.

## 6. CI

`.github/workflows/ci.yml`: `ruff check` + `ruff format --check` + `mypy src` +
`pytest tests/unit`, plus a gitleaks job, on every push and PR. The Postgres
service-container integration job is added when the Supabase backend lands.

## 7. Milestones (revised)

The original Phase 0–4 plan was revised (see the design revisions) to build the
**Open-Nexus runtime with FakeProvider first**, not "Nexus with Claude first."

- **Phase 0 — Harness skeleton:** contracts, config, terminal channel, gateway,
  core loop, FakeProvider/EchoProvider, SQLite memory, trace logging, CI.
  **DoD:** `uv run open-nexus chat` → echo reply, both turns stored in SQLite,
  `uv run pytest tests/unit` green, CI green. *(This phase is done.)*
- **Phase 1 — Provider runtime:** Anthropic + OpenAI + local adapters, router,
  capabilities, fallback chain, streaming. Contract tests every adapter passes.
- **Phase 2 — Persistent Nexus:** Supabase memory, identity loading, session
  resolution across channels, retrieval + summarisation, the API server.
- **Phase 3 — Tools & safety:** tool registry, safety policy, approval gate, tool
  run logs, read-only then write/external tools.
- **Phase 4 — Skills & delegation:** skill manifest + `SKILL.md` loader,
  `TaskPacket`, Jarvis hand-off, verification.
- **Phase 5 — Channels & scheduling:** Discord, Telegram, scheduler, daily
  briefing, event stream.
- **Phase 6 — Senses / remote control:** voice, screen, avatar, remote control.

## 8. Making changes safely

Branch names `phase-1/openai-adapter`; conventional commits (`feat:`/`fix:`/…);
the PR template asks what changed / how tested / what could break; ADRs in
`docs/adr/` for decisions worth second-guessing; tech debt logged as issues, not
folded into unrelated PRs.

## 9. Security & secrets

- `.env` gitignored from commit one; `.env.example` documents what's needed.
- **gitleaks** in pre-commit and CI; rotate any key that reaches a commit.
- **Supabase: RLS on every table, service-role key server-side only.** Clients go
  through Core, never direct to Supabase. (Moltbook leaked 1.5M keys this way.)
- CI secrets in GitHub Actions secrets; provider spend alerts at the dashboard.
- Deploy Core on a box you can physically unplug, with an egress allowlist.

## 10. Versioning

`v0.1.0` at the end of the provider-runtime phase (first usable Nexus); `v1.0.0`
when all senses are working, gated, and tested. Record the scheme in an ADR.
