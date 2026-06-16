-- Nexus memory schema (Supabase / Postgres)
-- ---------------------------------------------------------------------------
-- Layered memory, Hermes-style, backed by Postgres instead of SQLite so you get
-- FTS *and* pgvector semantic search in one store.
--
--   Layer 1 (core)         : nexus_memory + user_profile  — frozen per session
--   Layer 2 (history)      : messages                     — unbounded, searchable
--   Layer 3 (semantic)     : messages.embedding (pgvector)
--   Layer 4 (skills)       : later
--
-- SECURITY: enable Row-Level Security on EVERY table (see db/migrations and
-- docs/SECURITY.md). Never expose the service-role key to any client — all
-- clients go through Core. The most famous breach in this space leaked 1.5M keys
-- through a Supabase with public read/write and no RLS. Do not repeat it.
-- ---------------------------------------------------------------------------

create extension if not exists "pgcrypto";   -- gen_random_uuid()
create extension if not exists vector;        -- pgvector

-- WHO Nexus is talking to, across channels
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  display_name text,
  created_at timestamptz default now()
);

-- channel identities map to a user (you on Telegram == you on Discord)
create table if not exists channel_identities (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  channel text not null,            -- 'telegram' | 'discord' | 'slack' | 'web' | 'terminal'
  channel_user_id text not null,    -- platform-native id
  is_allowed boolean default false, -- per-channel allowlist (who may talk to Nexus)
  unique (channel, channel_user_id)
);

create table if not exists sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  channel text not null,
  started_at timestamptz default now(),
  last_active timestamptz default now()
);

-- Layer 2: unbounded, searchable conversation history
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id),
  role text not null,               -- 'user' | 'assistant' | 'tool'
  content text not null,
  tool_name text,
  created_at timestamptz default now(),
  fts tsvector generated always as (to_tsvector('english', content)) stored,
  embedding vector(1536)            -- pgvector; dimension must match EMBEDDING_DIM
);

create index if not exists messages_fts_idx on messages using gin (fts);
create index if not exists messages_embedding_idx on messages using ivfflat (embedding vector_cosine_ops);
create index if not exists messages_session_idx on messages (session_id, created_at);

-- Layer 1: curated, always-loaded core memory (hard token cap enforced in app)
create table if not exists nexus_memory (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  kind text not null,               -- 'fact' | 'preference' | 'note'
  content text not null,
  priority int default 0,
  updated_at timestamptz default now()
);

create table if not exists user_profile (
  user_id uuid primary key references users(id),
  profile jsonb not null default '{}'
);
