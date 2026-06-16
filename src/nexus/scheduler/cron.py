"""Cron — natural-language scheduled jobs in fresh isolated sessions (Hermes)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CronJob:
    """A scheduled job: when to run, what to do, and where to deliver results."""

    schedule: str          # natural language or cron expression
    instruction: str       # what Nexus should do
    deliver_to: str        # channel to route the result to


class CronScheduler:
    def __init__(self, *, core) -> None:
        self.core = core
        self._jobs: list[CronJob] = []

    def add(self, job: CronJob) -> None:
        self._jobs.append(job)

    async def run(self) -> None:
        """Run due jobs, each in a fresh isolated session; route results out."""
        # TODO(phase-2): parse schedules, fire jobs in isolated sessions,
        # deliver output to job.deliver_to.
        raise NotImplementedError("CronScheduler.run: Phase 2")
