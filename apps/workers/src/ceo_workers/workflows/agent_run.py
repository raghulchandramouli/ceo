"""Interactive agent-run workflow.

Database, HTTP, and model calls belong in activities. This module stays deterministic.
"""

from temporalio import workflow


@workflow.defn
class AgentRunWorkflow:
    @workflow.run
    async def run(self) -> None:
        return None
