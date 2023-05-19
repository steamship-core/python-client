from abc import ABC, abstractmethod
from typing import Any, List, Union

from steamship.agents.base import Action, AgentContext, BaseTool, FinishAction
from steamship.agents.parsers.base import OutputParser
from steamship.agents.tool import Tool


class Planner(ABC):
    class Config:
        arbitrary_types_allowed: True
        validation: False

    @abstractmethod
    def plan(self, tools: List[BaseTool], context: AgentContext) -> Union[Action, FinishAction]:
        pass


class LLMPlanner(Planner):
    class Config:
        arbitrary_types_allowed: True
        validation: False

    llm: Any  # placeholder for an LLM??
    # input_preparer: InputPreparer
    output_parser: OutputParser

    @abstractmethod
    def plan(self, tools: List[Tool], context: AgentContext) -> Action:
        # sketch...
        # prompt = PROMPT.format(input_preparer.prepare(context))
        # generation = llm.generate(prompt)
        # tool_name, inputs = output_parser.parse(generation)
        # return (tools[tool_name], inputs)
        pass
