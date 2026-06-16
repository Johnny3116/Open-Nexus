# HEARTBEAT

> The proactive-check checklist. On each heartbeat tick the scheduler wakes Nexus,
> which reviews this checklist against current context and **pings the user only
> if something is actually actionable** — otherwise it returns silently. This is
> OpenClaw's "only ping when something matters" model, which suits a home
> assistant better than a fixed-schedule cron.
>
> Nexus pings *you*. The homelab monitoring agents watch the *machines* — keep
> these concerns separate; the scheduler is a peer to the health sweep, not a
> duplicate of it.

## Check each tick

- [ ] Any follow-ups the user asked me to remember? (deadlines, "remind me when…")
- [ ] Any cron job that finished and has results worth surfacing?
- [ ] Anything in recent conversation left genuinely unresolved?
- [ ] Any time-sensitive note in `nexus_memory` coming due?

## Rules

- **Silence is the default.** If nothing on the list is actionable, return nothing.
- **Respect quiet hours** from `USER.md`.
- **One ping, batched.** Don't fire several messages in a tick; consolidate.
- **No spend without approval.** A heartbeat must never trigger a paid action on
  its own — that's how budgets get drained overnight.
