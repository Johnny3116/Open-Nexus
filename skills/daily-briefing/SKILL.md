---
name: daily-briefing
description: Assemble a short morning briefing and deliver it to a channel.
version: 0.1.0
author: nexus
trigger: "daily briefing", "what's on today", cron
tools: [memory, web_search, calendar, web_fetch]
trust: builtin
---

# Daily briefing

Built to run as a **cron** job in a fresh isolated session, delivering the result
to a chosen channel — but also usable on demand.

## Steps

1. Pull due/time-sensitive items from `nexus_memory` and any follow-ups.
2. Optionally gather a few headlines or weather if the user wants them.
3. Compose a short, scannable briefing (bullets, not prose).
4. Deliver to the configured channel; keep it to one message.

## Notes

- Respect quiet hours from `USER.md`.
- This is a *delivery* job (Hermes-style cron), distinct from the heartbeat's
  "only ping when something matters."
