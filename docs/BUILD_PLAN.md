# Nexus — Build Plan

The phased order in which Nexus gets built. The full design rationale (what we
take from OpenClaw vs Hermes, and why) is summarised below; the architecture
itself is in [`ARCHITECTURE.md`](ARCHITECTURE.md) and the security posture in
[`SECURITY.md`](SECURITY.md).

## One-line summary

> Nexus = OpenClaw's **channel-decoupled, file-owned identity** + Hermes'
> **layered retrieval memory and global personality**, backed by **your
> Supabase**, gated by **Hermes-style approvals**, scoped to
> **conversation/research/file-org**, and able to **hand coding to Jarvis** — so
> any model you plug in is still, unmistakably, Nexus.

## What we take from each

| Concern | Take from | Why |
|---|---|---|
| Personality is global, not per-workspace | Hermes | One Nexus, recognisable on every channel |
| Identity as an editable file you own (`SOUL.md`) | OpenClaw | Read and hand-tune it |
| Memory in a real queryable store, not files | Hermes → Supabase | Postgres + pgvector + FTS beats Markdown grep |
| Small frozen core + retrieve the rest on demand | Hermes | Token efficiency, cache stability, cheap model-swap |
| Skills as portable files (`agentskills.io`) | Both | Reuse community + your own Jarvis skills |
| Self-written procedural skills | Hermes (later) | Powerful, but earn it after basics work |
| Channel-decoupled core | OpenClaw | This decoupling *is* the harness |
| Safer-by-default: approval gates, isolation | Hermes | Non-negotiable given the tool surface |
| Heartbeat + cron for proactive behaviour | Both | "Ping only when it matters" + scheduled jobs |

## Build order

### Phase 0 — skeleton
Core loop + one provider (Claude) + terminal channel + Supabase `messages`
table. Prove **input → context → model → reply → store** works end to end.

### Phase 1 — the harness proper
Provider abstraction + fallback; `SOUL.md`/`USER.md`/`TOOLS.md` identity; layered
memory retrieval (FTS first, vectors second); add Telegram as the first real
channel. *Goal: same Nexus on terminal and Telegram, remembering across sessions.*

### Phase 2 — skills + scheduling
`SKILL.md` loader; research/file-organisation skills; heartbeat + cron;
`delegate_to_jarvis`.

### Phase 3 — the senses
Voice box (channel transform) → desktop widget → screen vision → remote control
(last, behind the hardest gates) → VTube avatar.

### Phase 4 — the Hermes luxuries
Self-written procedural skills; optional user-modelling layer. Only after
everything above is stable.

**Channels by effort:** terminal (trivial) < web UI < Telegram < Discord < Slack.

## Defaults chosen (open questions)

1. **Language:** Python (voice/vision/VTube + Supabase client + Hermes patterns).
2. **Where Core runs:** a dedicated homelab machine you can physically unplug —
   not your daily driver.
3. **Embedding model:** start hosted (quality), measure, move local if cost or
   privacy bites.
4. **Self-improving skills:** off until Phase 4. Earn it.
