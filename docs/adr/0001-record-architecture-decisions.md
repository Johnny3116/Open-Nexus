# 1. Record architecture decisions

- **Status:** accepted
- **Date:** 2026-06-16

## Context

Decisions we'll second-guess later (language, embedding model, file-vs-DB memory,
which channels) need a durable record so we don't re-litigate them in three months.

## Decision

Use lightweight ADRs: one short Markdown file per decision in `docs/adr/`, each
with Context, Decision, and Consequences. Numbered sequentially.

## Consequences

A greppable history of *why*. New contributors (and Jarvis) can read the trail
instead of reverse-engineering intent from the diff.
