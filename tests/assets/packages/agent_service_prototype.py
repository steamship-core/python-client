"""Intended to be a small, self-contained test of whether we can plumb various tool + task decompositions."""
from typing import Any, Dict, List, Union

from steamship import Block, SteamshipError, Task, TaskState
from steamship.agents.action import ToolAction
from steamship.agents.context import AgentContext
from steamship.agents.tool import Tool
from steamship.base.model import CamelModel
from steamship.client import Steamship
from steamship.invocable import InvocationContext, PackageService, create_handler, post


class ToolRegistry(CamelModel):
    available_tools: Dict[str, Tool]

    def get_tool(self, name: str) -> Tool:
        if name not in self.available_tools:
            raise SteamshipError(message=f"Tool {name} was not in registry")
        return self.available_tools[name]

    def add_tool(self, tool: Tool):
        self.available_tools[tool.name] = tool


class ToolThatAlwaysResponseSynchronouslyAndStatically(Tool):
    name = "ToolThatAlwaysResponseSynchronouslyAndStatically"
    ai_description = "ToolThatAlwaysResponseSynchronouslyAndStatically"
    human_description = "ToolThatAlwaysResponseSynchronouslyAndStatically"

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        return [Block(text="This was Synchronous and Static")]


class ToolThatAlwaysResponseSynchronouslyAndDynamically(Tool):
    name = "ToolThatAlwaysResponseSynchronouslyAndStatically"
    ai_description = "ToolThatAlwaysResponseSynchronouslyAndStatically"
    human_description = "ToolThatAlwaysResponseSynchronouslyAndStatically"

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        ret = []
        for block in tool_input:
            ret.append(
                Block(text=f"This was synchronous and Dynamic. Input block was: {block.text}")
            )
        return ret


class AgentService(PackageService):
    tool_registry: ToolRegistry

    def __init__(
        self,
        client: Steamship = None,
        config: Dict[str, Any] = None,
        context: InvocationContext = None,
    ):
        super().__init__(client, config, context)
        self.tool_registry.add_tool(ToolThatAlwaysResponseSynchronouslyAndStatically())
        self.tool_registry.add_tool(ToolThatAlwaysResponseSynchronouslyAndDynamically())

    @post("enqueue_tool_action")
    def enqueue_tool_action(self, action: ToolAction) -> Task:
        """Enqueues a ToolAction to eventually be performed.

        This should ALWAYS be the entrypoint to eventual action execution, as it inspects and wires any task
        dependencies correctly.
        """
        if isinstance(action, dict):
            action = ToolAction.parse_obj(action)

        input_state = action.input.state(self.client)

        if input_state == TaskState.failed:
            raise SteamshipError(
                message=f"Unable to enqueue ToolAction because input data is in state {input_state}."
            )

        return self.invoke_later(
            "run_tool_action",
            arguments={"action": action.dict()},
            wait_on_tasks=action.input.outstanding_task_dependencies(self.client),
        )

    @post("run_tool_action")
    def run_tool_action(self, action: ToolAction) -> ToolAction:
        """Runs a ToolAction immediately.

        This should only ever be called by a Task. That way the output is always recorded to a task.

        Input data readiness is assumed. If the input data is not ready at this stage, an exception is thrown.
        """
        agent_context = AgentContext()

        if isinstance(action, dict):
            action = ToolAction.parse_obj(action)

        input_state = action.input.state(self.client)

        if input_state != TaskState.succeeded:
            raise SteamshipError(
                message=f"Unable to run ToolAction because input data is in state {input_state}."
            )

        # Load the prior tool if appropriate
        prior_tool = None
        if action.input_tool_name:
            prior_tool = self.tool_registry.get_tool(action.input_tool_name)

        # Load the input blocks for this invocation
        tool_input = action.input.value(self.client, prior_tool)

        # Invoke!
        current_tool = self.tool_registry.get_tool(action.tool_name)
        output = current_tool.run(tool_input, agent_context)

        if isinstance(output, Task):
            action.output.task_id = output.task_id
        else:
            action.output.inline_value = output

        return action


handler = create_handler(AgentService)
