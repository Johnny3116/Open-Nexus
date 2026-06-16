-- 0001_initial — create the layered-memory tables.
-- Apply with: psql "$DATABASE_URL" -f db/migrations/0001_initial.sql
-- (or the Supabase MCP `apply_migration` tool).
--
-- This mirrors db/schema.sql. Keep them in sync, or generate one from the other.

\i db/schema.sql
