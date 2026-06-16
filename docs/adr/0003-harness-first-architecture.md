# 3. Harness-first architecture (contracts, gateway, safety; FakeProvider before Claude)

- **Status:** accepted
- **Date:** 2026-06-16

## Context

The first scaffold leaned toward "Nexus with Claude + Supabase first." That
couples the runtime to one model and one database, makes Phase 0 require keys and
Docker, and risks the provider layer quietly becoming the centre of the app
("a Claude wrapper with hobbies").

## Decision

Build **Open-Nexus the runtime** first, with these boundaries:

1. **Naming:** `open_nexus` = harness/runtime; *Nexus* = a persona (identity +
   config) that runs on it; *Jarvis* = the delegated coding agent.
2. **Contracts** (`contracts/`: message, provider, channel, tool, task) are owned
   by the harness. Providers and channels adapt *to* them; they don't define them.
3. **Gateway** (`gateway/`) owns auth/allowlist, normalisation, and session
   resolution. Channels are dumb adapters; core knows no channel.
4. **Providers** are config-driven (`config.yaml`) with `ProviderCapabilities` and
   a fallback chain. Adding an AI/API = adapter + config, not a core change.
5. **Memory** is an interface with SQLite (Phase 0, zero setup) and Supabase
   (later) backends.
6. **Safety** owns the approval gate: tools declare `risk_level`, safety enforces.
7. **Observability** + **RuntimeState** exist from day one (trace every turn;
   thread state explicitly rather than via globals).
8. **Phase 0 uses FakeProvider/EchoProvider** — no keys, no Docker, no billing.
   Claude/OpenAI/local are the next phase. Slack is dropped until there's a reason.

## Consequences

Phase 0 runs anywhere immediately and proves the architecture, not provider
billing. The cost is more upfront structure (more packages, more stubs) before the
first "real" model call — accepted deliberately, since these seams are expensive
to retrofit once memory, tools, and multiple providers exist.
