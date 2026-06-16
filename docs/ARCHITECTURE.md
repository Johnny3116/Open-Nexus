# Nexus architecture

A single long-lived **Core** process (the harness), with everything else as
pluggable adapters around it. Language: **Python** (voice/vision/VTube ecosystem,
Supabase client, matches Hermes patterns).

```
                       ┌─────────────────────────────────────────┐
                       │                NEXUS CORE                 │
  CHANNELS             │   ┌───────────────┐                       │   PROVIDERS
  ┌──────────┐         │   │ Session/Queue │                       │   ┌────────────┐
  │ Telegram │◄───────►│   │  (per chat)   │                       │   │ Anthropic  │
  │ Discord  │         │   └──────┬────────┘                       │   │ OpenAI     │
  │ Slack    │  adapter│          │                                │   │ OpenRouter │
  │ Web UI   │  layer  │   ┌──────▼────────┐    ┌──────────────┐   │   │ Local/     │
  │ Terminal │         │   │ Context       │◄──►│ Memory layer │◄──┼──►│ Ollama     │
  └──────────┘         │   │ Assembler     │    │ (Supabase)   │   │   └────────────┘
                       │   └──────┬────────┘    └──────────────┘   │
  IDENTITY             │          │                                │   SCHEDULER
  ┌──────────┐         │   ┌──────▼────────┐                       │   ┌────────────┐
  │ SOUL.md  │────────►│   │  Agent Loop   │                       │   │ Heartbeat  │
  │ (global) │         │   │ (model→tools→ │                       │   │ + Cron     │
  └──────────┘         │   │  loop→reply)  │                       │   └────────────┘
                       │   └──────┬────────┘                       │
                       │   ┌──────▼────────┐   ┌───────────────┐   │
                       │   │ Tool Runtime  │   │ Skill Loader  │   │
                       │   │ (+approval    │   │ (SKILL.md,    │   │
                       │   │  gate)        │   │  on demand)   │   │
                       │   └──────┬────────┘   └───────────────┘   │
                       └──────────┼────────────────────────────────┘
                                  │
        ┌─────────────┬───────────┼───────────┬──────────────┬─────────────┐
        ▼             ▼           ▼           ▼              ▼             ▼
   Desktop      Remote PC    Screen        Voice box     VTube        Delegate
   widget       control      capture/      (TTS/STT)     avatar       → JARVIS
                             vision                       control      (heavy coding)
```

## The Core / agent loop (`src/nexus/core/`)

Standard ReAct loop, kept boring and well-instrumented. Each turn: resolve
session → assemble context → call provider → if tool calls, run them through the
approval gate → feed results back → repeat to completion → emit reply on the
originating channel. A per-session queue serialises concurrent messages so "a
message arrives mid-run" is handled cleanly (OpenClaw's design).

## Identity layer (`identity/`, `src/nexus/identity/`)

One global `SOUL.md` in slot #1 of the system prompt on every turn, every
channel, every model. Provider-portable pure natural language. `TOOLS.md` (tool
conventions) and `USER.md` (your profile) sit beside it. The personality lives in
*your* prompt assembly, not the model.

## Provider abstraction (`src/nexus/providers/`)

One internal message format; adapters translate to/from each provider. Every
provider is treated as an OpenAI-compatible-or-translated endpoint, so cloud and
local look identical to Core. Config-driven model selection with a fallback chain
+ exponential backoff. Small, stable context keeps prompt-caching warm and model
swaps cheap.

## Channel layer (`src/nexus/channels/`)

One adapter per surface. Each: normalise inbound → common format, enforce a
per-channel allowlist, serialise replies out. Channels are fully decoupled from
the model and tools — this decoupling *is* the product.

## Memory (`src/nexus/memory/`, `db/`)

Layered, Hermes-style, backed by Supabase (Postgres + pgvector + FTS):

- **Layer 1 — Core (frozen per session):** curated `nexus_memory` + `user_profile`,
  hard token cap (~1–2k). Memory-flush extracts durable facts before compaction.
- **Layer 2 — Conversation history (unbounded, searchable):** every turn stored;
  retrieved on demand via FTS + vector similarity, summarised back into the loop.
- **Layer 3 — Semantic / long-term:** embeddings over messages + extracted facts.
- **Layer 4 — Skills (procedural):** later.

Retrieval per turn: Layer 1 (all, capped) + Layer 2 (top-k FTS + top-k vector,
deduped, summarised) → assemble → call model.

## Scheduling (`src/nexus/scheduler/`)

- **Heartbeat** (OpenClaw): review `HEARTBEAT.md`, ping only if something matters.
- **Cron** (Hermes): natural-language jobs in fresh isolated sessions, results
  routed to a channel.

A peer to the homelab's machine-monitoring sweep, not a duplicate.

## Senses (`src/nexus/senses/`)

Desktop widget, remote control, screen/vision, voice box, VTube avatar. Each goes
through the approval gate. See the package docstring for build order and gating.

## Delegation (`src/nexus/delegation/`)

`delegate_to_jarvis`: hand build/fix/refactor tasks to Jarvis, monitor, report
back in Nexus's own voice. Two specialists, one front door.
