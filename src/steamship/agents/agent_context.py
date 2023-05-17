import contextlib
import json
import logging
from abc import ABC, abstractmethod
from time import sleep
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import Field

from steamship import Block, PluginInstance, Steamship, SteamshipError, Task, TaskState, Workspace
from steamship.base.model import CamelModel

# There's a circular import if we import this; I figure we can just solve
# with a base class,  but I'm just going to use Any so that I can move on with the prototyping.

Tool_ = Any
ToolOutput_ = Union[
    List[Block],  # A list of blocks
    List[Task[List[Block]]],  # A list of tasks that each produce a list of blocks
]


def get_me_blocks(obj: Any):
    if isinstance(obj, Task):
        if isinstance(obj.output, dict) and obj.output.get("blocks"):
            return obj.output.get("blocks")
        elif hasattr(obj.output, "blocks"):
            return obj.output.blocks
    return obj


class ToolRequest(CamelModel):
    previous_tool: str  # This is my hack to call the "Post-process" function
    name: str  # The name of the tool
    payload: Task


class AgentContext(CamelModel, ABC):
    client: Steamship = Field(None, exclude=True)
    tools: Dict[str, Tool_] = {}

    def add_tool(self, tool: Tool_):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool_:
        if name in self.tools:
            return self.tools[name]
        raise SteamshipError(message=f"Tool {name} not found in Agent Context.")

    @abstractmethod
    def run_tool(
        self, name: str, blocks: ToolOutput_, calling_tool: Optional[Tool_] = None
    ) -> Task[List[Block]]:
        pass

    @abstractmethod
    def update_blocks(self, blocks: List[Block]):
        pass

    @abstractmethod
    def append_log(self, message: str):
        pass

    @abstractmethod
    def default_text_generator(self) -> PluginInstance:
        pass

    @classmethod
    @contextlib.contextmanager
    def temporary(cls, client: Optional[Steamship] = None) -> "AgentContext":
        client = client or Steamship()
        workspace = Workspace.create(client=client)
        context = cls(client=client)
        yield context
        workspace.delete()


class DebugAgentContext(AgentContext):
    client: Steamship = Field(None, exclude=True)

    def update_blocks(self, blocks: List[Block]):
        pass

    def append_log(self, message: str):
        print(f"[LOG] {message}")

    def default_text_generator(self) -> PluginInstance:
        return self.client.use_plugin("gpt-4", config={"model": "gpt-3.5-turbo"})

    def loudly_wait_task(self, task: Task):
        self.append_log("Awaiting Task since this is the DevelopmentContext.")
        self.append_log(f"Task State: {task.state} / {task.task_id}")
        while task.state in [TaskState.waiting, TaskState.running]:
            sleep(2)
            task.refresh()
            self.append_log(f"Task State: {task.state} / {task.task_id}")

    def run_tool(
        self, name: str, tool_input: ToolOutput_, calling_tool: Optional[Tool_] = None
    ) -> Task[List[Block]]:
        """Runs the tool on the provided blocks. Since this is the debug context, awaits an incompleted task if
        that is what was provided.

        It's important that run_tool accept a Task as input -- this lets run_tool work with the output of another
        tool that has emitted a Task, whether it is running or waiting or succeeded.
        """
        self.append_log(f"Running tool {name}")

        if isinstance(tool_input, Task):
            self.loudly_wait_task(tool_input)
            # Quick of the way the dev environment is set up; we DON'T run the post-processing here since it was
            # already run.
            tool_input = tool_input.output

        tool = self.get_tool(name)

        really_blocks = []
        for block in tool_input:
            # Note: The problem is that we don't always marshall engine responses automatically.
            if isinstance(block, dict):
                print("Boo. It's a dict that should have been a block")
                really_blocks.append(Block.parse_obj(block))
            else:
                really_blocks.append(block)

        tool_input = really_blocks
        tool_output = tool.run(tool_input, self)

        if isinstance(tool_output, Task):
            self.loudly_wait_task(tool_output)
            # Quick of the way the dev environment is set up; we DON'T run the post-processing here since it was
            # already run.
            if tool_output.output:
                tool_output = tool_output.output
            else:
                # TODO: There's a bug in the /echo task where it doesn't echo! So we have to use the input as a backup until we fix it
                # as the MapConcat tool uses echo
                tool_output.output = json.loads(tool_output.input).get("blocks", [])
                tool_output = tool.post_process(tool_output, self)

        blocks = []
        for task_or_block in tool_output:
            if isinstance(task_or_block, Task):
                task = cast(Task[List[Block]], task_or_block)
                self.append_log(f"Received Task {task.task_id} as tool output.")
                self.loudly_wait_task(task)
                self.append_log("Awaited Task. Converting to blocks.")
                postprocessed_blocks = tool.post_process(task, self)
                for block in postprocessed_blocks:
                    blocks.append(block)
            else:
                blocks.append(task_or_block)
        return Task(state=TaskState.succeeded, output=blocks)


class ProductionAgentContext(AgentContext):
    client: Steamship = Field(None, exclude=True)

    def update_blocks(self, blocks: List[Block]):
        pass

    def append_log(self, message: str):
        """TODO: Append to production logs with additional metadata."""
        logging.info(message)

    def default_text_generator(self) -> PluginInstance:
        return self.client.use_plugin("gpt-4", config={"model": "gpt-3.5-turbo"})

    def run_tool(
        self, name: str, tool_input: List[Block], calling_tool: Optional[Tool_] = None
    ) -> ToolOutput_:
        """Runs the tool on the provided blocks. If it is a task for blocks, schedules the running later."""
        self.append_log(f"Running tool {name}")

        if isinstance(tool_input, Task):
            self.append_log(
                "Received Task for future blocks as tool input. Since this is the DevelopmentContext, awaiting blocks synchronously."
            )
            task = cast(Task[List[Block]], tool_input)

            if task.state == TaskState.failed:
                msg = f"Unable to run Tool {name} on output of failed task {task.task_id}: {task.status_message}"
                self.append_log(msg)
                raise SteamshipError(message=msg)
            elif task.state in [TaskState.waiting, TaskState.running]:
                msg = f"Deferring run Tool {name} on Task in state {task.state}, ID: {task.task_id}"
                self.append_log(msg)
                return self.schedule_future_run(name, tool_input)
            else:
                # Task was successful
                msg = f"Loaded block output for input to Tool {name} from Task in state {task.state}, ID: {task.task_id}"
                self.append_log(msg)
                tool_input = task.output

        tool = self.get_tool(name)
        tool_output = tool.run(tool_input, self)
        return tool_output

    def schedule_future_run(self, name: str, tool_input: List[Block]) -> ToolOutput_:
        """Schedules the future running of a tool.."""
        self.append_log(f"Running tool {name}")

        if isinstance(tool_input, Task):
            self.append_log(
                "Received Task for future blocks as tool input. Since this is the DevelopmentContext, awaiting blocks synchronously."
            )
            task = cast(Task[List[Block]], tool_input)
            task.wait()
            self.append_log("Awaiting async blocks and resolving.")
            tool_input = task.output

        tool = self.get_tool(name)
        tool_output = tool.run(tool_input, self)
        return tool_output
