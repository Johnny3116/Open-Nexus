# Nexus — Harness Design

*A model-agnostic conversational agent for the homelab. Plug in any LLM, keep one
personality, one memory, one set of skills and tools.* This doc is **what** we
build; `nexus-build-plan.md` is **how**.

> Naming: **Open-Nexus** is the harness/runtime (the `open_nexus` package).
> **Nexus** is the assistant persona that runs on it (identity files + config).
> **Jarvis** is the delegated coding agent. One runtime, one personality, coding
> handed off.

---

## 1. The two reference systems

Two systems made **opposite architectural bets**. Nexus copies neither blindly.

### OpenClaw — the control-plane bet
- One long-lived gateway daemon owns everything: channel connections, sessions,
  the agent loop, model calls, tool execution, memory.
- Identity & memory are plain Markdown files (`SOUL.md`, `USER.md`, `TOOLS.md`,
  `MEMORY.md`, `HEARTBEAT.md`) injected into context each turn — inspectable,
  greppable, git-versionable.
- Skills are human-authored `SKILL.md` files, loaded on demand.
- Heartbeat scheduler wakes the agent to act unprompted.
- Model-agnostic via a provider config with rotation + backoff failover.
- Reputation: popular but a 2026 security cautionary tale — a cluster of CVEs, 21k+
  exposed instances, 26% of community skills carrying a vulnerability, and a sister
  project (Moltbook) leaking 1.5M API keys through a misconfigured Supabase with
  public read/write and no RLS. See §6.

### Hermes — the runtime/learning bet
- The agent loop itself is the core; gateway, cron, tooling, persistence sit
  *around* it.
- **Layered memory:** small curated frozen core (hard token cap) + unbounded
  searchable history (SQLite/FTS) summarised on demand + optional user-model layer
  + skills as procedural memory the agent writes itself.
- `SOUL.md` is global to the instance — one personality everywhere.
- Cron in natural language; jobs run in fresh isolated sessions.
- Safer by default: user authorisation, dangerous-command approval, container
  isolation, credential filtering, context-file scanning, SSRF protection.

### The shared skeleton
`input → assemble context → call model → execute tool calls → feed results back →
repeat → reply`, wrapped in a persistent process with channels, memory,
scheduling, and a skill/prompt layer loaded on demand. Nexus is another instance
of this skeleton; the interesting choices are *what wraps it*.

---

## 2. What Nexus takes from each

| Concern | From | Why |
|---|---|---|
| Personality global, not per-workspace | Hermes | One Nexus on every channel |
| Identity as a file you own (`SOUL.md`) | OpenClaw | Read and hand-tune it |
| Memory in a real queryable store | Hermes → Supabase | Postgres + pgvector + FTS beats Markdown grep |
| Small frozen core + retrieve on demand | Hermes | Token efficiency, cache stability, cheap model-swap |
| Skills as portable files | Both | Reuse community + own skills |
| Self-written skills | Hermes (later) | Earn it after basics work |
| Channel-decoupled core | OpenClaw | The decoupling *is* the harness |
| Safer-by-default approvals + isolation | Hermes | Non-negotiable given the tool surface |
| Heartbeat + cron | Both | "Ping when it matters" + scheduled jobs |

---

## 3. Architecture (as built)

A single long-lived **Core** with everything else as pluggable adapters. Language:
**Python 3.13**. The revised module layout (see `nexus-build-plan.md` and the §15
revisions) keeps contracts, gateway, and safety as first-class layers:

```
channels (dumb)  →  gateway (auth/normalise/session)  →  core loop
                                                            │
        contracts (message/provider/channel/tool/task)      │
        providers (router + adapters) ◄─────────────────────┤
        memory (sqlite | supabase)  ◄───────────────────────┤
        safety (policy + approval gate) ◄───────────────────┤
        tools / skills / scheduler / observability ◄─────────┘
```

- **Contracts** are owned by the harness; providers and channels adapt *to* them.
- **Gateway** owns auth, normalisation, and session resolution. Channels are dumb.
- **Providers** are config-driven with capabilities + a fallback chain. Adding an
  AI/API is an adapter + config, never a core-loop change.
- **Memory** is an interface: SQLite for Phase 0 (zero setup), Supabase later.
- **Safety** owns the approval gate: tools *declare* risk, safety *enforces* it.
- **Observability** traces every lifecycle event by `trace_id` from day one.

### 3.6 Memory — layered (Supabase in the persistent phase)
- **Layer 1 — Core (frozen per session):** curated `nexus_memory` + `user_profile`,
  hard token cap (~1–2k). Memory-flush extracts durable facts before compaction.
- **Layer 2 — History (unbounded, searchable):** every turn; retrieved via FTS +
  vector similarity, summarised back into the loop.
- **Layer 3 — Semantic:** embeddings over messages + extracted facts.
- **Layer 4 — Skills (procedural):** later.

The Postgres schema lives in `src/open_nexus/memory/schema.sql` (RLS enabled +
forced on every table).

### 3.8 The special tools (differentiators)
Desktop widget; remote computer control (the hardest gate, suggest-and-confirm);
screen capture/vision (opt-in per session, never silent); voice box (TTS/STT as a
channel transform); VTube avatar (small declarative cues). Each goes through the
approval gate.

### 3.9 Nexus ↔ Jarvis delegation
Coding is carved out of Nexus and made a first-class tool: `delegate_to_jarvis`
hands a well-formed `TaskPacket` to Jarvis, monitors it, and reports back in
Nexus's voice. Two specialists, one front door.

---

## 6. Security — read before writing a line

The tool surface (remote control + screen + voice + autonomous heartbeat +
shell-capable skills) is exactly what made OpenClaw a cautionary tale.

- **Lock down Supabase.** RLS on every table; service-role key server-side only;
  all clients go through Core; keep the project off the public internet. (The
  Moltbook breach leaked 1.5M keys via public read/write + no RLS.)
- **Gate every irreversible/external action** behind explicit human approval.
- **Treat every skill you didn't write as untrusted.** Fork, read, install.
- **Isolate.** Core on its own VM/container with an egress allowlist, on a box you
  can physically unplug.
- **Pin and patch**; **set provider spend alerts** at the provider dashboard.

---

## 7. One-line summary

Nexus = OpenClaw's channel-decoupled, file-owned identity + Hermes' layered
retrieval memory and global personality, backed by your Supabase, gated by
Hermes-style approvals, scoped to conversation/research/file-org, and able to hand
coding to Jarvis — so any model you plug in is still, unmistakably, Nexus.
