"""Run the interactive and sync workers in one process for local development."""

import asyncio
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from temporalio.client import Client
from temporalio.worker import Worker

from ceo_workers.workflows.agent_run import AgentRunWorkflow
from ceo_workers.workflows.connector_sync import ConnectorSyncWorkflow

WORKFLOWS: dict[str, list[type]] = {
    "agent-queue": [AgentRunWorkflow],
    "sync-queue": [ConnectorSyncWorkflow],
}
QUEUES = tuple(WORKFLOWS)


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    temporal_address: str = "localhost:7233"
    temporal_namespace: str = "default"


async def connect(settings: WorkerSettings) -> Client:
    log = logging.getLogger("ceo_workers")
    while True:
        try:
            return await Client.connect(
                settings.temporal_address,
                namespace=settings.temporal_namespace,
            )
        except Exception as exc:
            log.warning(
                "Temporal is not ready at %s (%s); retrying in 2s",
                settings.temporal_address,
                exc,
            )
            await asyncio.sleep(2)


async def run_queue(client: Client, task_queue: str, workflows: list[type]) -> None:
    worker = Worker(client, task_queue=task_queue, workflows=workflows)
    await worker.run()


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    settings = WorkerSettings()
    client = await connect(settings)
    logging.getLogger("ceo_workers").info("worker started queues=%s", ",".join(QUEUES))
    async with asyncio.TaskGroup() as group:
        for task_queue, workflows in WORKFLOWS.items():
            group.create_task(run_queue(client, task_queue, workflows))
