# Security — read this before you write a line

Nexus's tool surface (remote control + screen + voice + autonomous heartbeat +
shell-capable skills) is *exactly* the combination that made OpenClaw a
cautionary tale in early 2026 — a cluster of CVEs (incl. a CVSS 9.9), 21,000+
instances exposed on the public internet, 26% of community skills carrying a
vulnerability, 230+ malicious skills uploaded in a single week, and a sister
project leaking **1.5M API keys** through a misconfigured Supabase with public
read/write and no row-level security. The defaults below are not optional.

## 1. Lock down Supabase

- **RLS on every table.** See `db/migrations/0002_rls.sql` — RLS is enabled and
  *forced* on every table, with no permissive policies. Only the service-role key
  (which bypasses RLS) can read/write, and it lives server-side in Core.
- **Never expose the service-role key to any client.** The widget, web UI, and
  every channel adapter go through Core — never directly to Supabase.
- **Keep secrets server-side.** They live in `.env` (gitignored), referenced by
  name from `config/nexus.toml`. Never in the TOML, never in a client bundle.
- **Don't put the project on the public internet** without knowing exactly why.

## 2. Gate every irreversible or external action

Behind explicit human approval: remote-control clicks/keystrokes, file deletes,
sending messages/emails on your behalf, anything that spends money. This is
Hermes' dangerous-command approval layer, implemented in
`src/nexus/tools/approval.py` and configured under `[tools].approval_required`.
Default to *suggest-and-confirm*.

## 3. Treat every skill you didn't write as untrusted code

26% of audited community skills carried a vulnerability; 230+ malicious ones
shipped in a week. **Fork, read, then install. No auto-install from a registry.**
The `SkillLoader` carries a `trust` field per skill (`builtin` / `reviewed` /
`untrusted`) — default to `untrusted`.

## 4. Isolate

- Core on its own VM/container with a network **egress allowlist**.
- Screen and remote-control scoped to one machine, opt-in per session, never
  silent (`ScreenCapture` refuses to capture until explicitly enabled).
- Run Core on a dedicated homelab machine you can **physically unplug** — not your
  daily driver. Shell + remote-control access wants isolation and a kill switch.

## 5. Pin and patch

This category ships CVEs fast (nine in four days, once). Pin dependency versions,
watch advisories for whatever you build on.

## 6. Set provider spend alerts

At the **provider level**, not just in config. A misconfigured heartbeat interval
can drain a budget overnight — a heartbeat must never trigger a paid action on
its own (enforced as policy in `scheduler/heartbeat.py`).
