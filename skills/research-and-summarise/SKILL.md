---
name: research-and-summarise
description: Research a topic across sources and return a tight, cited summary.
version: 0.1.0
author: nexus
trigger: "research", "look into", "summarise this topic", "what's the latest on"
tools: [web_search, web_fetch, memory]
trust: builtin
---

# Research and summarise

Use this when the user wants a quick, trustworthy read on a topic rather than a
deep multi-day report.

## Steps

1. Clarify scope in one line if the ask is broad (timeframe, depth, region).
2. Fan out a handful of searches; fetch the most credible 3–6 sources.
3. Cross-check any claim that matters before stating it as fact.
4. Return: a 3–5 bullet summary, then sources as a short list.
5. Offer to store key findings in `nexus_memory` if they're durably useful.

## Notes

- Keep it tight. The user asked for a summary, not a transcript.
- Flag disagreement between sources rather than papering over it.
- For a *deep*, multi-source, fact-checked report, this is the wrong skill —
  hand off to a dedicated research flow instead.
