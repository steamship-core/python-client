from abc import ABC, abstractmethod
from typing import Union

from pydantic import BaseModel

from steamship.agents.base import Action, AgentContext, FinishAction


class InputParser(BaseModel, ABC):
    # This takes multi-media and converts into a textual form useful for prompting
    # for further text generation.
    #
    # example:
    #  - input: AgentContext(completed_steps: [Step(dall-e, prompt, output_block)])
    #  - output: "Action: Dall-E Tool
    #             ActionInput: prompt
    #             ActionOutput: Block(UUID)"
    @abstractmethod
    def prepare(self, context: AgentContext) -> str:
        pass


class OutputParser(BaseModel, ABC):
    # Example image-based workflow:
    # (1) user request: generate an image of a row-house in a city street.
    # (2) llm planner: dalle("row-house in a city street")
    # (3) dall-e tool: output=block(02342342342)
    # (4) package response: <image>
    # (5) user request: make the door of the house red/
    # (6) llm planner: pix-to-pix(prompt="make door red", block=02423452345)
    # (7) pix-2-pix tool: output=block(992341234)
    #
    # In this flow, the LLM planner needs to tell the pix-2-pix tool which image to start with, so it has to know how
    # to represent that in text.
    #
    # example:
    #  - input: "Action: Pix-2-Pix
    #            ActionInput: Block(UUID)"
    #  - output: ("pix-to-pix", [Block(UUID)])
    @abstractmethod
    def parse(self, text: str, context: AgentContext) -> Union[Action, FinishAction]:
        pass
