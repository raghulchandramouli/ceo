"""Backfill and incremental cursor sync.

Fetch and upsert work belongs in activities. This module stays deterministic.
"""

from temporalio import workflow


@workflow.defn
class ConnectorSyncWorkflow:
    @workflow.run
    async def run(self) -> None:
        return None
