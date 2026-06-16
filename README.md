# Open-Nexus

> A model-agnostic conversational agent **harness**. Plug in any LLM, keep one
> personality, one memory, one set of skills and tools.

**Open-Nexus** is the harness/runtime. **Nexus** is the assistant persona that
runs on it (the files in `identity/` + your `config.yaml`). **Jarvis** is the
delegated coding agent. The personality, memory, skills, and tools live in *this*
harness, not in the model — swap Claude for GPT for a local Ollama model and
Nexus is still, unmistakably, Nexus.

```
Open-Nexus = harness/runtime        (the open_nexus package)
Nexus      = your assistant/persona (identity/ + config.yaml)
Jarvis     = delegated coding agent (heavy lifting handed off)
```

It blends two reference systems: OpenClaw's channel-decoupled, file-owned identity
and Hermes' layered retrieval memory + global personality — gated by Hermes-style
approvals, scoped to conversation/research/file-org. See
[`docs/nexus-harness-design.md`](docs/nexus-harness-design.md) (what) and
[`docs/nexus-build-plan.md`](docs/nexus-build-plan.md) (how).

---

## Quick start (Phase 0 — no keys, no Docker)

Phase 0 runs on an **echo provider** and **SQLite**, so it works immediately with
zero cloud setup. It proves the architecture, not provider billing.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # install uv (Rust binary)
uv sync                                            # build env (fetches Python 3.13)
uv run open-nexus chat                             # terminal channel, echo provider
```

```
$ uv run open-nexus chat
Open-Nexus ready (model: echo). Ctrl-D or /quit to exit.
you> hello there
nexus> echo: hello there
```

Both turns are stored in `nexus.sqlite`. To use a real model, copy the config and
set a key:

```bash
cp config.example.yaml config.yaml   # set default: claude (or gpt / ollama)
cp .env.example .env                  # add ANTHROPIC_API_KEY etc.
uv run open-nexus chat
```

---

## Architecture

A single long-lived **Core**, with everything else as pluggable adapters. The
boundaries are first-class:

```
channels (dumb)
   │  normalise in / serialise out
   ▼
gateway ── auth/allowlist · session resolution · rate limit · RuntimeState
   │
   ▼
core loop ── assemble context → call provider → run tools (via safety) → reply
   │              │                    │                  │
   │         context             providers           safety
   │      (SOUL slot #1)     (router + adapters,    (policy + approval
   │                          capabilities,          gate; tools declare
   │                          fallback chain)        risk, safety enforces)
   ▼
memory (sqlite | supabase)        observability (trace every lifecycle event)
```

- **`contracts/`** — message/provider/channel/tool/task types, owned by the
  harness. Providers and channels adapt *to* them.
- **`gateway/`** — the only layer that knows both channels and core.
- **`providers/`** — config-driven; adding an AI/API is an adapter + config.
- **`memory/`** — SQLite now, Supabase (Postgres + pgvector + FTS) later.
- **`safety/`** — the approval gate; nothing irreversible fires without it.

---

## Repository layout

```
src/open_nexus/
├── contracts/     # message, provider, channel, tool, task — the harness's vocabulary
├── gateway/       # inbound, outbound, router, auth, rate_limit
├── core/          # loop, session, context
├── providers/     # base, fake, anthropic, openai, local, router, factory
├── channels/      # base, terminal (+ web/telegram/discord stubs)
├── memory/        # base, sqlite_store, supabase_store, retrieval, schema.sql
├── safety/        # policy, approval, risk
├── observability/ # events, trace, logger
├── tools/         # base, registry, delegate_jarvis, research, files, + senses stubs
├── skills/        # loader (skill.toml + SKILL.md)
├── scheduler/     # heartbeat, cron
├── api/           # FastAPI server (later phase)
├── runtime/       # RuntimeState
├── config.py      # secrets from env + provider routing from YAML
└── app.py         # entrypoint: `open-nexus chat`
identity/          # SOUL.md / USER.md / TOOLS.md / HEARTBEAT.md — edit by hand
skills/            # SKILL.md + skill.toml per skill
tests/             # unit (FakeProvider seam) + integration (marked)
docs/              # design, build plan, ADRs
```

---

## Build order

| Phase | Deliverable |
|---|---|
| **0 — Harness skeleton** ✅ | contracts, gateway, core loop, FakeProvider, SQLite, traces, CI |
| **1 — Provider runtime** | Anthropic/OpenAI/local adapters, router, capabilities, fallback, streaming |
| **2 — Persistent Nexus** | Supabase memory, identity loading, retrieval, API server |
| **3 — Tools & safety** | registry, approval gate, read-only → write/external tools |
| **4 — Skills & delegation** | skill loader, `TaskPacket`, Jarvis hand-off |
| **5 — Channels & scheduling** | Discord, Telegram, heartbeat + cron, daily briefing |
| **6 — Senses / remote control** | voice, screen, avatar, remote control (hardest gate) |

---

## Developing

```bash
uv run pytest tests/unit       # fast, deterministic (FakeProvider seam)
uv run ruff check . && uv run ruff format --check .
uv run mypy src
uv run pre-commit install      # ruff + gitleaks on every commit
```

CI (`.github/workflows/ci.yml`) runs all of the above plus gitleaks on every push
and PR. See [`docs/nexus-build-plan.md`](docs/nexus-build-plan.md) §9 for the
security rules (RLS everywhere, service-role key server-side only, gate every
irreversible action, untrusted-by-default skills).

## License

TBD.
