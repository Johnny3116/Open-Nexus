# Nexus

> A model-agnostic conversational agent for the homelab. Plug in any LLM, keep
> one personality, one memory, one set of skills and tools.

Nexus is a harness — an [OpenClaw](https://en.wikipedia.org/wiki/Agent)/Hermes-style
agent runtime — built around a single idea: **the personality, memory, skills,
and tools live in *your* harness, not in the model.** Swap Claude for GPT for a
local Ollama model and Nexus is still, unmistakably, Nexus.

```
Nexus = OpenClaw's channel-decoupled, file-owned identity
      + Hermes' layered retrieval memory and global personality
      + your Supabase (Postgres + pgvector + FTS)
      + Hermes-style approval gates
      + scoped to conversation / research / file-org
      + able to hand coding off to Jarvis
```

---

## Why this exists

Two reference systems made **opposite architectural bets**:

- **OpenClaw** — one long-lived gateway daemon owns everything; identity and
  memory are plain Markdown files you can read, grep, and git-version; skills are
  human-authored `SKILL.md` files. Channel-decoupled, model-agnostic — but a
  2026 security cautionary tale (a sister project leaked 1.5M API keys through a
  misconfigured Supabase).
- **Hermes** — the agent loop *is* the core; memory is layered (small frozen
  core + searchable SQLite history + semantic recall + self-written skills);
  personality is global to the instance; safer-by-default with approval gates and
  isolation.

Nexus deliberately takes the best of each rather than copying either. See
[`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) for the full design rationale and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the component map.

| Concern | Borrowed from |
|---|---|
| Personality is **global**, not per-workspace | Hermes |
| Identity as an **editable file you own** (`SOUL.md`) | OpenClaw |
| Memory in a **real queryable store** (Postgres) | Hermes → Supabase |
| Small **frozen core context** + retrieve the rest on demand | Hermes |
| Skills as **portable `SKILL.md` files** | Both |
| **Channel-decoupled** core (swap channel ↔ model, nothing else changes) | OpenClaw |
| **Safer-by-default**: approval gates, isolation, credential filtering | Hermes |
| **Heartbeat + cron** for proactive behaviour | Both |

---

## Architecture at a glance

A single long-lived **Core** process (the harness) with everything else as
pluggable adapters around it.

```
   CHANNELS              NEXUS CORE                    PROVIDERS
  ┌──────────┐      ┌──────────────────────┐         ┌─────────────┐
  │ Terminal │      │  Session / Queue     │         │ Anthropic   │
  │ Web UI   │◄────►│  Context Assembler   │◄───────►│ OpenAI      │
  │ Telegram │      │  Agent Loop          │         │ OpenRouter  │
  │ Discord  │      │  Tool Runtime + gate │         │ Local/Ollama│
  │ Slack    │      │  Skill Loader        │         └─────────────┘
  └──────────┘      └──────────┬───────────┘
                               │                       SCHEDULER
   IDENTITY                    │                      ┌─────────────┐
  ┌──────────┐                 │                      │ Heartbeat   │
  │ SOUL.md  │─────────────────┤                      │ + Cron      │
  │ USER.md  │                 │                      └─────────────┘
  │ TOOLS.md │          ┌──────▼───────┐
  └──────────┘          │ Memory layer │  ◄──►  Supabase (Postgres
                        │ (Supabase)   │         + pgvector + FTS)
                        └──────────────┘
            │
  ┌─────────┴──────────────────────────────────────────────────┐
  ▼          ▼          ▼          ▼          ▼          ▼
Desktop   Remote     Screen     Voice box  VTube     Delegate
widget    control    /vision    (TTS/STT)  avatar    → JARVIS
```

The interesting choices are *what wraps the loop*. The loop itself is a boring,
well-instrumented ReAct cycle:

```
input → assemble context → call model → execute tool calls
      → feed results back → repeat → reply
```

---

## Repository layout

```
.
├── identity/              # The files that make Nexus "Nexus" — edit by hand
│   ├── SOUL.md            #   global personality (system-prompt slot #1)
│   ├── USER.md            #   your profile & preferences
│   ├── TOOLS.md           #   tool conventions
│   └── HEARTBEAT.md       #   proactive-check checklist
├── db/
│   ├── schema.sql         # full Postgres schema (Supabase)
│   └── migrations/        # ordered migrations
├── config/
│   └── nexus.example.toml # copy to nexus.toml, fill in
├── skills/                # portable SKILL.md files (agentskills.io standard)
│   ├── research-and-summarise/
│   ├── file-triage/
│   └── daily-briefing/
├── src/nexus/
│   ├── core/              # agent loop, session, per-session queue, context assembler
│   ├── providers/         # provider abstraction (anthropic/openai/openrouter/local)
│   ├── channels/          # one adapter per surface (terminal/web/telegram/discord/slack)
│   ├── memory/            # Supabase-backed layered memory + retrieval + embeddings
│   ├── identity/          # SOUL/USER/TOOLS loader
│   ├── skills/            # on-demand SKILL.md loader
│   ├── tools/             # tool registry, runtime, and the approval gate
│   ├── scheduler/         # heartbeat + cron
│   ├── senses/            # voice, screen/vision, remote control, widget, vtube
│   └── delegation/        # delegate_to_jarvis
├── docs/                  # ARCHITECTURE, SECURITY, BUILD_PLAN
└── tests/
```

---

## Quick start (Phase 0 skeleton)

> ⚠️ Nexus is in active scaffolding. The structure is in place; modules are
> stubs with clearly marked `TODO`s. Build order is in
> [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md).

```bash
# 1. Python 3.11+ recommended
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Configure
cp config/nexus.example.toml config/nexus.toml
cp .env.example .env            # add provider keys + Supabase URL/keys
$EDITOR config/nexus.toml .env

# 3. Provision the database (Supabase / Postgres)
#    apply db/schema.sql to your project, then enable RLS (see docs/SECURITY.md)

# 4. Run the terminal channel
python -m nexus run --channel terminal
```

---

## Build order

| Phase | Deliverable |
|---|---|
| **0 — skeleton** | Core loop + Claude provider + terminal channel + `messages` table end-to-end |
| **1 — the harness** | Provider abstraction + fallback; `SOUL/USER/TOOLS` identity; layered memory retrieval; Telegram channel |
| **2 — skills + scheduling** | `SKILL.md` loader; research/file-org skills; heartbeat + cron; `delegate_to_jarvis` |
| **3 — the senses** | Voice (channel transform) → desktop widget → screen vision → remote control → VTube avatar |
| **4 — Hermes luxuries** | Self-written procedural skills; optional user-modelling layer |

Channels by effort: **terminal < web UI < Telegram < Discord < Slack.**

---

## Security — read before writing a line

Nexus's tool surface (remote control + screen + voice + autonomous heartbeat +
shell-capable skills) is *exactly* the combination that made OpenClaw a
cautionary tale. The defaults are not optional — see
[`docs/SECURITY.md`](docs/SECURITY.md). In short:

- **Lock down Supabase.** RLS on every table; never expose the service-role key
  to any client; all clients go through Core, never direct to Supabase; keep the
  project off the public internet.
- **Gate every irreversible or external action** behind explicit human approval.
- **Treat every skill you didn't write as untrusted code.** Fork, read, install —
  no auto-install from a registry.
- **Isolate.** Core on its own VM/container with an egress allowlist, on a machine
  you can physically unplug.
- **Set provider spend alerts** at the provider level, not just in config.

---

## License

TBD.
