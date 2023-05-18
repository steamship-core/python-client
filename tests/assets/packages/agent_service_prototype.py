"""Intended to be a small, self-contained test of whether we can plumb various tool + task decompositions."""
import base64
import json
import logging
from typing import Any, Callable, Dict, List, Union

from steamship import Block, SteamshipError, Task, TaskState
from steamship.agents.action import ToolAction
from steamship.agents.context import AgentContext
from steamship.agents.tool import Tool
from steamship.agents.tool_data import ToolData
from steamship.base.model import CamelModel
from steamship.client import Steamship
from steamship.invocable import InvocationContext, PackageService, create_handler, post


def b64_decode(task: Task) -> Any:
    b64_output = task.output
    binary_output = base64.b64decode(b64_output)
    string_output = binary_output.decode("utf-8")
    json_output = json.loads(string_output)
    return json_output


class ToolRegistry(CamelModel):
    available_tools: Dict[str, Tool] = {}

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
    name = "ToolThatAlwaysResponseSynchronouslyAndDynamically"
    ai_description = "ToolThatAlwaysResponseSynchronouslyAndDynamically"
    human_description = "ToolThatAlwaysResponseSynchronouslyAndDynamically"

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        ret = []
        for block in tool_input:
            ret.append(
                Block(text=f"This was synchronous and Dynamic. Input block was: {block.text}")
            )
        return ret


class ToolThatDynamicallyPlansMoreAsyncWork(Tool):
    name = "ToolThatDynamicallyPlansMoreAsyncWork"
    ai_description = "ToolThatDynamicallyPlansMoreAsyncWork"
    human_description = "ToolThatDynamicallyPlansMoreAsyncWork"

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        # First let's call the static async tool!
        dyamic_plan_step_1 = ToolAction(
            tool_name="ToolThatAlwaysResponseAsynchronouslyAndStatically", input=ToolData()
        )

        # This ToolAction represents the eventual completion of this step.
        dyamic_plan_step_1_output = context.invoke_tool(dyamic_plan_step_1)
        logging.info(
            f"{self.name}: Output ToolData of Tool1 Invoke was {dyamic_plan_step_1_output.output}"
        )

        # Now let's call the dynamic async tool... providing it the input of the prior tool!
        # We don't need to do any manipulation of input since the broader system guarantees
        # everything is [Block] -> [Block].

        # This is the key magic right here. We can just set step2.input = step1.output and it works.. even
        # thought none of the actual processing has been done, or data created.

        # Note how the ToolData object also has a carve-out for a file_id. This isn't yet pursued in the unit
        # tests on this branch but added to illustrate the map-reduce scenario: in which the initiator of the map
        # operation synchronously (1) creates a file. and (2) spawns TONS of tasks. then (3) writes those task IDs
        # to the file. THEN it schedules a future ToolAction that depends on those tasks, and takes as input the ToolData
        # defined by that file's ID. That means that next ToolAction (1) only happens when the map operations are done, and
        # (2) is passed, automatically, as its input, a set of blocks containing the UUIDs of the tasks with the results.
        dymamic_plan_step_2 = ToolAction(
            tool_name="ToolThatAlwaysResponseAsynchronouslyAndDynamically",
            input=dyamic_plan_step_1_output.output,
        )

        # Now let's invoke THAT tool.. in the future!
        dynamic_plan_step_2_output = context.invoke_tool(dymamic_plan_step_2)
        logging.info(
            f"{self.name}: Output ToolData of Tool2 Invoke was {dynamic_plan_step_2_output.output}"
        )

        # And finally we'll just return the task of the FINAL result.

        # It's actually much cooler: we can POST PROCESS it! But since this is going to be the terminus
        # in the task chain, and we don't have the magic postprocessing step at the very end, I won't add more fancy
        # stuff there.
        task = Task(task_id=dynamic_plan_step_2_output.output.task_id)
        logging.info(f"{self.name}: Returning Task {task.task_id}")
        return task

    def post_process(self, async_task: Task[Any], context: AgentContext) -> List[Block]:
        """The echo function we're using Base64 encodes the task."""
        logging.info(
            f"Tool {self.name} post-processing task {async_task.task_id} output {async_task.output}"
        )
        obj = b64_decode(async_task)
        return obj.get("obj")


class ToolThatAlwaysResponseAsynchronouslyAndStatically(Tool):
    name = "ToolThatAlwaysResponseAsynchronouslyAndStatically"
    ai_description = "ToolThatAlwaysResponseAsynchronouslyAndStatically"
    human_description = "ToolThatAlwaysResponseAsynchronouslyAndStatically"

    echo: Callable[[List[Block]], Task]

    def __input__(self, echo: Callable[[List[Block]], Task]):
        self.echo = echo

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        """NOTE: We don't serialize things well here, requiring the dict() method, which stinks."""
        return self.echo([Block(text="This was Asynchronous and Static").dict()])

    def post_process(self, async_task: Task[Any], context: AgentContext) -> List[Block]:
        """The echo function we're using Base64 encodes the task."""
        logging.info(
            f"Tool {self.name} post-processing task {async_task.task_id} output {async_task.output}"
        )
        obj = b64_decode(async_task)
        return obj.get("obj")


class ToolThatAlwaysResponseAsynchronouslyAndDynamically(Tool):
    name = "ToolThatAlwaysResponseAsynchronouslyAndDynamically"
    ai_description = "ToolThatAlwaysResponseAsynchronouslyAndDynamically"
    human_description = "ToolThatAlwaysResponseAsynchronouslyAndDynamically"

    echo: Callable[[List[Block]], Task]

    def __input__(self, echo: Callable[[List[Block]], Task]):
        self.echo = echo

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        ret = []
        for block in tool_input:
            ret.append(
                Block(text=f"This was asynchronous and Dynamic. Input block was: {block.text}")
            )
        return self.echo([block.dict() for block in ret])

    def post_process(self, async_task: Task[Any], context: AgentContext) -> List[Block]:
        """The echo function we're using Base64 encodes the task."""
        logging.info(
            f"Tool {self.name} post-processing task {async_task.task_id} output {async_task.output}"
        )
        obj = b64_decode(async_task)
        return obj.get("obj")


class AgentService(PackageService):
    tool_registry: ToolRegistry

    def __init__(
        self,
        client: Steamship = None,
        config: Dict[str, Any] = None,
        context: InvocationContext = None,
    ):
        super().__init__(client, config, context)

        def echo(obj: Any) -> Task:
            return self.invoke_later("echo", arguments={"obj": obj})

        self.tool_registry = ToolRegistry()
        self.tool_registry.add_tool(ToolThatAlwaysResponseSynchronouslyAndStatically())
        self.tool_registry.add_tool(ToolThatAlwaysResponseSynchronouslyAndDynamically())
        self.tool_registry.add_tool(ToolThatAlwaysResponseAsynchronouslyAndStatically(echo=echo))
        self.tool_registry.add_tool(ToolThatAlwaysResponseAsynchronouslyAndDynamically(echo=echo))
        self.tool_registry.add_tool(ToolThatDynamicallyPlansMoreAsyncWork())

    @post("echo")
    def echo(self, obj: dict) -> dict:
        """Used to help create simple async scenarios requiring postprocessing."""
        return {"obj": obj}

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

        task_dependencies = action.input.outstanding_task_dependencies(self.client)
        task_dependencies_ids = (
            [] if task_dependencies is None else [task.task_id for task in task_dependencies]
        )

        task = self.invoke_later(
            "run_tool_action",
            arguments={"action": action.dict()},
            wait_on_tasks=action.input.outstanding_task_dependencies(self.client),
        )

        logging.info(
            f"Enqueued ToolAction Task {task.task_id} for tool {action.tool_name} with dependencies: {task_dependencies_ids}."
        )

        return task

    @post("run_tool_action")
    def run_tool_action(self, action: ToolAction) -> ToolAction:
        """Runs a ToolAction immediately.

        This should only ever be called by a Task. That way the output is always recorded to a task.

        Input data readiness is assumed. If the input data is not ready at this stage, an exception is thrown.
        """

        # Wire up agent_context with a callback that is capable of scheduling an invocation of a tool
        agent_context = AgentContext()

        def invoke_tool(tool_action: ToolAction) -> ToolAction:
            # See this is doubly async. We invoke later the enqueueing.
            task = self.invoke_later(
                "enqueue_tool_action", arguments={"action": tool_action.dict()}
            )
            output_action = ToolAction.parse_obj(tool_action.dict())
            output_action.output = ToolData(task_id=task.task_id)
            logging.info(
                f"AgentContext: invoke_tool called on {tool_action.tool_name} resulting in task {output_action.output.task_id}. {output_action}"
            )
            return output_action

        agent_context.invoke_tool = invoke_tool

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
        logging.info(f"Running tool {current_tool.name} on input {tool_input}")
        tool_output = current_tool.run(tool_input, agent_context)
        logging.info(f"Tool {current_tool.name} produced output {tool_output}")

        if action.output is None:
            action.output = ToolData()

        if isinstance(tool_output, Task):
            action.output.task_id = tool_output.task_id
        else:
            action.output.inline_value = tool_output

        return action


handler = create_handler(AgentService)
