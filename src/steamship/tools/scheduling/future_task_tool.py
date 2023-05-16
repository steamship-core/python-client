from typing import List

from steamship import Block, Steamship, Tag, Task
from steamship.agents.agent_context import AgentContext
from steamship.agents.agents import Tool


class FutureTaskTool(Tool):
    name: str = "TaskScheduler"
    human_description: str = "Schedule async calls to a package."
    ai_description: str = "Used to schedule reminders for the user at a future point in time."
    instance_handle: str
    method: str
    verb: str = "POST"

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        """Schedules a call to a Steamship method in the future.

        Inputs
        ------
        input: List[Block]
            A list of blocks to be rewritten if text-containing.
        context: AgentContext
            The active AgentContext.

        Output
        ------
        output: List[Blocks]
            A list of blocks whose content has been rewritten.
        """

        # parse and call _schedule_task
        task = self._schedule_task(context.client, "some-time-in-future", {"arg1": "foo"})
        return [
            Block(
                text="Your task has been scheduled.",
                tags=[Tag(kind="Task ID", value={"task_id", task.task_id})],
            )
        ]

    def _schedule_task(self, client: Steamship, task_kwargs: dict) -> Task:
        task_delay_ms = 10
        payload = {
            "instanceHandle": self.instance_handle,
            "payload": {
                "httpVerb": self.verb,
                "invocationPath": self.method,
                "arguments": task_kwargs,
            },
        }
        return client.post(
            "package/instance/invoke",
            payload,
            task_delay_ms=task_delay_ms,
        )
