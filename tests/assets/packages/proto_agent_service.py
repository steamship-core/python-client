"""Intended to be a small, self-contained test of whether we can plumb various tool + task decompositions."""
import json
from typing import Any, Dict, List, Optional, Union, cast

from steamship import Block, File, SteamshipError, Task, TaskState
from steamship.agents.context import AgentContext
from steamship.agents.tool import Tool
from steamship.base.model import CamelModel
from steamship.client import Steamship
from steamship.invocable import (
    InvocableResponse,
    InvocationContext,
    PackageService,
    create_handler,
    post,
)


class ToolRegistry(CamelModel):
    available_tools: Dict[str, Tool]

    def get_tool(self, name: str) -> Tool:
        if name not in self.available_tools:
            raise SteamshipError(message=f"Tool {name} was not in registry")
        return self.available_tools[name]

    def add_tool(self, tool: Tool):
        self.available_tools[tool.name] = tool


def task_output_as_blocks(task: Task) -> List[Block]:
    # Note: this would want to be a less brittle implementation, but the assumption here is that,
    # without a post-processor, (1) the output MUST be a list of blocks, and (2) it will be stored in
    # the Task as a string.
    return [cast(Block, Block.parse_obj(block_dict)) for block_dict in json.loads(task.output)]


class ToolBinding(CamelModel):
    """The combination of a Tool and its Input"""

    tool_name: str  # Tool Name

    # The tool input may be an inlined list of blocks.
    tool_input_inline: Optional[List[Block]]

    # The tool input may be the output of a known file.
    tool_input_file: Optional[str]  # UUID

    # The tool input may be the output of a known task.
    tool_input_task: Optional[str]  # UUID

    # If tool input is a task, optional tool to peform post-processing
    tool_input_task_postprocesor: Optional[str]  # Tool Name

    # OUTPUT

    # The tool output may be inlined
    tool_output_inline: Optional[List[Block]]

    # The tool output may be the result of a task
    tool_output_task: Optional[str]

    def get_tool_input(self, client: Steamship, tool_registry: ToolRegistry) -> List[Block]:
        """Return the tool input, which may be inline, in a file, or the result of a task + optional post-processing."""
        if self.tool_input_inline:
            return self.tool_input_inline
        elif self.tool_input_file:
            file = File.get(client, _id=self.tool_input_file)
            return file.blocks
        elif self.tool_input_task:
            task = Task.get(client, _id=self.tool_input_task)
            if self.tool_input_task_postprocesor:
                return tool_registry.get(self.tool_input_task_postprocesor).post_process(task)
            else:
                return task_output_as_blocks(task)

    def get_tool_output(
        self, client: Steamship, tool_registry: ToolRegistry, post_process: bool = False
    ) -> List[Block]:
        """Return the tool output.

        There is an edge case: the FINAL step of a chain may require post-processing upon egress. But upon ingress
        this can be handled on the get_tool_input side of things.

        This edge case wouldn't exist if we just always had the tool post-process upon completion, but we need it to be
        upon the start of the next task, or retrieval of the final value, since that's the moment when we resume control
        from some externalized task (3rd party call, blockification, etc) that is unaware of the nature of this post-processing.
        """
        if self.tool_output_inline:
            return self.tool_input_inline
        elif self.tool_output_task:
            task = Task.get(client, _id=self.tool_output_task)
            if post_process:
                return tool_registry.get(self.tool_name).post_process(task)
            else:
                return task_output_as_blocks(task)

    def is_input_ready(self, client: Steamship) -> bool:
        if self.tool_input_inline:
            return True
        elif self.tool_input_file:
            return True  # Uncertain here.
        elif self.tool_input_task:
            task = Task.get(client, _id=self.tool_input_task)
            return task.state == TaskState.succeeded

    def is_output_ready(self, client: Steamship) -> bool:
        if self.tool_output_inline:
            return True
        elif self.tool_output_task:
            task = Task.get(client, _id=self.tool_output_task)
            return task.state == TaskState.succeeded


class Executor(CamelModel):
    client: Steamship
    tool_registry: ToolRegistry

    def __init__(self, client: Steamship):
        super().__init__()
        self.client = client
        self.tool_registry = ToolRegistry()

    def run(
        self, tool_binding: ToolBinding, context: AgentContext
    ) -> Union[List[Block], Task[Any]]:
        tool_input = tool_binding.get_tool_input(self.client, self.tool_registry)
        tool = self.tool_registry.get(tool_binding.tool_name)
        result = tool.run(tool_input, context)
        return result


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
    executor: Executor

    def __init__(
        self,
        client: Steamship = None,
        config: Dict[str, Any] = None,
        context: InvocationContext = None,
    ):
        super().__init__(client, config, context)
        self.executor = Executor(self.client)
        self.executor.tool_registry.add_tool(ToolThatAlwaysResponseSynchronouslyAndStatically())
        self.executor.tool_registry.add_tool(ToolThatAlwaysResponseSynchronouslyAndDynamically())

    def _register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    @post("echo")
    def echo(self, **kwargs) -> InvocableResponse[dict]:
        return kwargs

    @post("run_tool")
    def run_tool(self, binding: ToolBinding) -> ToolBinding:
        """Always return a Task that resolves to the eventual output of the workplan, even if the workplan was synchronous.

        For ease of experimentation, I'm using ToolBinding as the envelope that wraps all requests and responses.
        """
        result = self.executor.run(binding)

        if isinstance(result, Task):
            binding.tool_output_task = result.task_id
            return binding
        else:
            binding.tool_output_inline = result
            return binding


handler = create_handler(AgentService)
