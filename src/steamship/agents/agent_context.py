import contextlib
import logging
from abc import ABC, abstractmethod
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
    def run_tool(self, name: str, blocks: ToolOutput_, calling_tool: Optional[Tool_] = None):
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

    def run_tool(
        self, name: str, tool_input: ToolOutput_, calling_tool: Optional[Tool_] = None
    ) -> ToolOutput_:
        """Runs the tool on the provided blocks. Since this is the debug context, awaits an incompleted task if
        that is what was provided."""
        self.append_log(f"Running tool {name}")

        blocks = []

        for item in tool_input:
            if isinstance(item, Task):
                task = cast(Task[List[Block]], item)
                self.append_log(f"Received Task {task.task_id} as tool input.")
                self.append_log("Awaiting Task since this is the DevelopmentContext.")
                task.wait()
                self.append_log("Awaited Task. Converting to blocks.")
                postprocessed_blocks = calling_tool.post_process(task)
                for block in postprocessed_blocks:
                    blocks.append(block)
                    self.append_log(f"Intermediate output: {block.text}")
            else:
                blocks.append(item)

        tool = self.get_tool(name)
        tool_output = tool.run(blocks, self)
        return tool_output


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
