from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from steamship import Block
from steamship.agents.agents import AgentContext


class Tool(BaseModel, ABC):
    name: str
    human_description: str
    ai_description: str

    @abstractmethod
    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        pass
