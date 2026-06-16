# 2. Python 3.13 + uv toolchain

- **Status:** accepted
- **Date:** 2026-06-16

## Context

The harness leans on the Python ML/voice/vision ecosystem and the Supabase
client. We need a fast, reproducible env/dependency workflow.

## Decision

- **Python 3.13**, pinned in `.python-version` (conservative floor; longest track
  record; every dependency supports it).
- **uv** for env + deps + lockfile + task running; `uv.lock` is committed.
- **Ruff** (lint + format), **mypy** (types), **pytest + pytest-asyncio** (tests).

## Consequences

`uv sync --frozen` gives identical envs locally and in CI. Switching to Python
3.14 later is a one-line `.python-version` change plus a re-lock.
