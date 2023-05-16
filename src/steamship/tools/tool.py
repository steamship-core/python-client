from abc import ABC, abstractmethod
from typing import List, Optional, Union

from pydantic import BaseModel

from steamship import Block, Task
from steamship.agents.agent_context import AgentContext


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
    def run(
        self, tool_input: List[Block], context: AgentContext
    ) -> Union[List[Block], Task[List[Block]]]:
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


class GeneratorTool(Tool):
    """
    A base class for tools that wrap Steamship Generator plugins. Subclass this and implement
    the `accept_output_block` method.
    """

    generator_plugin_handle: str
    generator_plugin_instance_handle: Optional[str] = None
    generator_plugin_config: dict = {}

    @abstractmethod
    def accept_output_block(self, block: Block) -> bool:
        raise NotImplementedError()

    def run(
        self, tool_input: List[Block], context: AgentContext
    ) -> Union[List[Block], Task[List[Block]]]:
        generator = context.client.use_plugin(
            plugin_handle=self.generator_plugin_handle,
            instance_handle=self.generator_plugin_instance_handle,
            config=self.generator_plugin_config,
        )

        output = []
        for block in tool_input:
            if not block.is_text():
                continue

            prompt = block.text
            task = generator.generate(text=prompt, append_output_to_file=True)
            task.wait()
            blocks = task.output.blocks
            for output_block in blocks:
                if self.accept_output_block(output_block):
                    output.append(output_block)

        return output


class ImageGeneratorTool(GeneratorTool):
    """
    A base class for tools that wrap Steamship Image Generator plugins.
    """

    def accept_output_block(self, block: Block) -> bool:
        return block.is_image()


class AudioGeneratorTool(GeneratorTool):
    """
    A base class for tools that wrap Steamship Audio Generator plugins.
    """

    def accept_output_block(self, block: Block) -> bool:
        return block.is_audio()
