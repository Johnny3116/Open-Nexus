"""Open-Nexus — a model-agnostic conversational agent harness.

Open-Nexus is the harness/runtime. *Nexus* is the assistant persona that runs on
it (identity files + config). *Jarvis* is the delegated coding agent. The
personality, memory, skills, and tools live in this harness, not in the model —
swap the provider and Nexus is still, unmistakably, Nexus.

See docs/nexus-harness-design.md (what we build) and docs/nexus-build-plan.md
(how we build it).
"""

__version__ = "0.0.1"
