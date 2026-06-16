-- 0002_rls — lock everything down.
-- ---------------------------------------------------------------------------
-- Enable Row-Level Security on EVERY table. All access goes through Core using
-- the service-role key (server-side only), so by default no anon/public access
-- is granted here. If you later add a client that authenticates as a Supabase
-- user, add explicit, scoped policies — never a blanket `using (true)`.
--
-- The 1.5M-key breach in this space was a Supabase with public read/write and no
-- RLS. This migration is the antidote. See docs/SECURITY.md.
-- ---------------------------------------------------------------------------

alter table users               enable row level security;
alter table channel_identities  enable row level security;
alter table sessions            enable row level security;
alter table messages            enable row level security;
alter table nexus_memory        enable row level security;
alter table user_profile        enable row level security;

-- Force RLS even for table owners, so a leaked anon/publishable key can't read.
alter table users               force row level security;
alter table channel_identities  force row level security;
alter table sessions            force row level security;
alter table messages            force row level security;
alter table nexus_memory        force row level security;
alter table user_profile        force row level security;

-- No policies are defined on purpose: with RLS enabled and no policy, only the
-- service-role key (which bypasses RLS) can access these tables. Core uses that
-- key, server-side. Add scoped policies only if/when a real client needs direct
-- access — and review them against docs/SECURITY.md first.
