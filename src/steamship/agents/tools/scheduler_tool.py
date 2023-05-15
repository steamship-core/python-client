from typing import List

from steamship import Block, Steamship, Tag, Task
from steamship.agents.agents import AgentContext
from steamship.agents.tools.workspace_tool import WorkspaceTool


class TaskScheduler(WorkspaceTool):
    name = "TaskScheduler"
    human_description = "Schedule async calls to a package"
    ai_description = ("Used to schedule reminders for the user at a future point in time.",)

    def __init__(self, client: Steamship, instance_handle: str, method: str):
        super().__init__(client=client)
        self._handle = instance_handle
        self._method = method

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        # parse and call _schedule_task
        task = self._schedule_task("some-time-in-future", {"arg1": "foo"})
        return [
            Block(
                text="Your task has been scheduled.",
                tags=[Tag(kind="Task ID", value={"task_id", task.task_id})],
            )
        ]

    def _schedule_task(self, time: str, task_kwargs: dict) -> Task:
        url = self.client._url(operation="package/instance/invoke")
        payload = {
            "instanceHandle": self._handle,
            "payload": {
                "httpVerb": "POST",
                "invocationPath": self._method,
                "arguments": task_kwargs,
            },
        }
        return self._call(url, payload, time)

    def _call(self, url, payload, schedule_time) -> Task:
        # does the steamship-appropriate calling function.
        pass
