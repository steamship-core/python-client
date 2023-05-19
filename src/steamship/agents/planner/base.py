from abc import ABC, abstractmethod
from typing import List, Union, Any

from pydantic import BaseModel

from steamship.agents.base import AgentContext
from steamship.agents.base import BaseTool
from steamship.agents.base import FinishAction, Action
from steamship.agents.parsers.base import OutputParser


class Planner(BaseModel, ABC):
    tools: List[BaseTool]

    @abstractmethod
    def plan(self, context: AgentContext) -> Union[Action, FinishAction]:
        pass


class LLMPlanner(Planner):
    llm: Any
    # input_preparer: InputPreparer
    output_parser: OutputParser

    @abstractmethod
    def plan(self, context: AgentContext) -> Action:
        # sketch...
        # prompt = PROMPT.format(input_preparer.prepare(context))
        # generation = llm.generate(prompt)
        # tool_name, inputs = output_parser.parse(generation)
        # return (tools[tool_name], inputs)
        pass
