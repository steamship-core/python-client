import json
from abc import ABC, abstractmethod
from typing import List, Optional, Union

import requests
from pydantic import BaseModel

from steamship import Block, File, MimeTypes, Task
from steamship.agents.agent_context import AgentContext

ToolOutput = Union[
    List[Block],  # A list of blocks
    List[Task[List[Block]]],  # A list of tasks that each produce a list of blocks
]


class Tool(BaseModel, ABC):
    """
    A base class for capabilities used by the agent. Subclass this and implement the `run` method as well as the
    following class attributes:

    Attributes
    ----------

    name: str
        A performative name that will be used for your tool in the prompt to the agent. For instance
        `"text-classifier"` or `"image_generator"`.
    ai_description: str
        A short description of what your tool does, the inputs it expects and the output(s) it
        will return. For instance 'This is a tool that downloads a file from a `url`. It takes the `url` as input, and
        returns the text contained in the file'. This description acts as documentation for LLM-directed invocation of
        the tool and should be though of as something for which prompt engineering is required.
    human_description: str
        A short description of what your tool does, for explanation to a human user. It
        should return a description of the tool's purpose, inputs, and outputs, but it need not be thought of as a
        prompt-engineering exercise.
    """

    name: str
    human_description: str
    ai_description: str

    @abstractmethod
    def run(self, tool_input: List[Block], context: AgentContext) -> ToolOutput:
        """Runs the tool in the provided context.

        Intended semantics of the `run` operation:
        * It always produces some output, expressed as a list of Blocks.
        * It is allowed to have side effects, via the `context` object.
        * It is allowed to initiate long-running asynchronous operations, via the `context` object.

        Inputs
        ------

        input: List[Block]
            A list of Blocks provided as input to the tool.
        context: AgentContext
            The context in which the tool is operating, including short-term conversational memory, long-term
            searchable memory, and read-write workspace operations.

        Outputs
        -------

        output: List[Block]
            The output of this tool

        """
        raise NotImplementedError()

    def register_in_context(self, context: AgentContext):
        """Register this tool in the context.
        Necessary because some tools need to register their sub-tools as well (like the SeriesTool).

        Note: Potential for naming conflicts here. What we really need is potentially a hierarchical namespace.
        Obj/Obj/Obj
        """
        context.add_tool(self)

    def post_process(self, task: Task, context: AgentContext) -> List[Block]:
        """Called after this Tool returns a Task, to finalize the output into a set of blocks."""
        return task.output


class ScrapeAndBlockifyTool(Tool):
    """
    A base class for tools that wrap Steamship Blockifier plugin which transforms bytes to a set of blocks.
    """

    blockifier_plugin_handle: str
    blockifier_plugin_instance_handle: Optional[str] = None
    blockifier_plugin_config: dict = {}

    @abstractmethod
    def should_blockify(self, block: Block) -> bool:
        raise NotImplementedError()

    def get_mime_type(self):
        return None

    def _scrape(self, url: str, context: AgentContext) -> File:
        response = requests.get(url)
        file = File.create(context.client, content=response.content, mime_type=self.get_mime_type())
        return file

    def run(self, tool_input: List[Block], context: AgentContext) -> ToolOutput:
        tasks = []

        blockifier = context.client.use_plugin(
            plugin_handle=self.blockifier_plugin_handle,
            instance_handle=self.blockifier_plugin_instance_handle,
            config=self.blockifier_plugin_config,
        )

        for input_block in tool_input:
            if not input_block.is_text():
                continue

            url = input_block.text
            file = self._scrape(url, context)
            task = file.blockify(blockifier.handle)
            tasks.append(task)

        return tasks

    def post_process(self, task: Task, context: AgentContext) -> List[Block]:
        """In this case, the Blockifier returns a BlockAndTagResponse that has a .file.blocks method on it"""
        try:
            return task.output.file.blocks
        except BaseException:
            return json.loads(task.output).get("file", {}).get("blocks")


class ImageBlockifierTool(ScrapeAndBlockifyTool):
    """
    A base class for tools that wrap Steamship Image Blockifier plugins.
    """

    def get_mime_type(self):
        return MimeTypes.PNG

    def should_blockify(self, block: Block) -> bool:
        return block.is_image()


class AudioBlockifierTool(ScrapeAndBlockifyTool):
    """
    A base class for tools that wrap Steamship Audio Blockifier plugins.
    """

    def get_mime_type(self):
        return MimeTypes.MP3

    def should_blockify(self, block: Block) -> bool:
        return block.is_audio()
