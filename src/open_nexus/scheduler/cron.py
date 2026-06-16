"""Cron — natural-language scheduled jobs in fresh isolated sessions."""

from __future__ import annotations

from pydantic import BaseModel


class CronJob(BaseModel):
    schedule: str  # natural language or cron expression
    instruction: str  # what Nexus should do
    deliver_to: str  # channel to route the result to


class CronScheduler:
    def __init__(self) -> None:
        self._jobs: list[CronJob] = []

    def add(self, job: CronJob) -> None:
        self._jobs.append(job)

    async def run(self) -> None:
        # TODO(phase: scheduling): fire due jobs in isolated sessions, deliver out.
        raise NotImplementedError("CronScheduler.run: scheduling phase")
