from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel

from steamship import Block
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

    def init(
        self,
        name: Optional[str] = None,
        ai_description: Optional[str] = None,
        human_description: Optional[str] = None,
    ) -> List[Block]:
        # Permit instance creators to override registration fields.

        # QUESTION: Do we need these to be static? Playing with this design to enable someone to create a tool
        # that is intended to be parameterized by the tool invoker; e.g. a prompt rewriting tool.

        if name:
            self.name = name
        if ai_description:
            self.ai_description = ai_description
        if human_description:
            self.human_description = human_description

    @abstractmethod
    def run(self, input: List[Block], context: AgentContext) -> List[Block]:
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
