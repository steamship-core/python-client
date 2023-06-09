from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from steamship.agents.schema.action import Action
from steamship.agents.schema.context import AgentContext
from steamship.agents.schema.llm import LLM
from steamship.agents.schema.output_parser import OutputParser
from steamship.agents.schema.tool import Tool


class Agent(BaseModel, ABC):
    """Agent is responsible for choosing the next action to take for an AgentService.

    It uses the provided context, and a set of Tools, to decide on an action that will
    be executed by the AgentService.
    """

    tools: List[Tool]
    """Tools that can be used by the Agent in selecting the next Action."""

    @abstractmethod
    def next_action(self, context: AgentContext) -> Action:
        pass


class LLMAgent(Agent):
    """LLMAgents choose next actions for an AgentService based on interactions with an LLM."""

    llm: LLM
    """The LLM to use for action selection."""

    output_parser: OutputParser
    """Utility responsible for converting LLM output into Actions"""

    @abstractmethod
    def next_action(self, context: AgentContext) -> Action:
        pass
