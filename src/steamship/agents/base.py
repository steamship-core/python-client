from abc import ABC, abstractmethod
from typing import List, Optional, Any, Union, Dict

from pydantic import BaseModel

from steamship import Block, Steamship
from steamship.agents.context import AgentContext
from steamship.agents.tools.base import BaseTool


class Action(BaseModel):
    tool: str  # Tools are retrieved via their name
    tool_input: str  # Tools always get strings as input


class FinishAction(BaseModel):
    response: Any  # Output can be anything as long as it's JSON serializable


class BaseAgent(BaseModel, ABC):
    tool_dict: Optional[Dict[str, BaseTool]] = []
    client: Steamship

    @abstractmethod
    def next_action(self, context: AgentContext) -> Union[Action, FinishAction]:
        pass

    @abstractmethod
    def execute_action(self, action: Action, context: AgentContext):
        pass

    @abstractmethod
    def run(self, agent_input: List[Block], context: AgentContext) -> List[Block]:
        pass
