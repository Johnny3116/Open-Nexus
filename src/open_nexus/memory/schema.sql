-- Open-Nexus memory schema (Supabase / Postgres) — Phase 1+.
-- Phase 0 uses SQLite (memory/sqlite_store.py); this is the persistent backend.
--
-- Layered memory: nexus_memory + user_profile (Layer 1, frozen core),
-- messages (Layer 2, searchable history via FTS), messages.embedding (Layer 3,
-- pgvector semantic recall).
--
-- SECURITY: RLS is enabled AND forced on every table, with no permissive
-- policies. Only the service-role key (which bypasses RLS, used server-side by
-- Core) can read/write. The 1.5M-key Moltbook breach was a Supabase with public
-- read/write and no RLS. Do not repeat it. See docs/nexus-build-plan.md §9.

create extension if not exists "pgcrypto";
create extension if not exists vector;

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  display_name text,
  created_at timestamptz default now()
);

-- you-on-Telegram == you-on-terminal: channel identities map to one user
create table if not exists channel_identities (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  channel text not null,
  channel_user_id text not null,
  is_allowed boolean default false,
  unique (channel, channel_user_id)
);

create table if not exists sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  channel text not null,
  started_at timestamptz default now(),
  last_active timestamptz default now()
);

create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id),
  role text not null,
  content text not null,
  tool_name text,
  created_at timestamptz default now(),
  fts tsvector generated always as (to_tsvector('english', content)) stored,
  embedding vector(1536)
);
create index if not exists messages_fts_idx on messages using gin (fts);
create index if not exists messages_embedding_idx on messages using ivfflat (embedding vector_cosine_ops);
create index if not exists messages_session_idx on messages (session_id, created_at);

-- Layer 1: curated, always-loaded core memory (hard token cap enforced in app)
create table if not exists nexus_memory (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  kind text not null,            -- 'fact' | 'preference' | 'note'
  content text not null,
  priority int default 0,
  updated_at timestamptz default now()
);

create table if not exists user_profile (
  user_id uuid primary key references users(id),
  profile jsonb not null default '{}'
);

-- Lock everything down. RLS enabled + forced, no policies => service-role only.
do $$
declare t text;
begin
  foreach t in array array[
    'users','channel_identities','sessions','messages','nexus_memory','user_profile'
  ] loop
    execute format('alter table %I enable row level security', t);
    execute format('alter table %I force row level security', t);
  end loop;
end $$;
