from abc import ABC, abstractmethod
from typing import Any, List, Union

from pydantic import BaseModel

from steamship import Block, Task
from steamship.agents.context import AgentContext


class BaseTool(BaseModel, ABC):
    name: str
    ai_description: str
    human_description: str  # Human readable string for logging

    @abstractmethod
    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        raise NotImplementedError()

    # This gets called later if you return Task[Any] from run
    def post_process(self, async_task: Task[Any]) -> List[Block]:
        # nice helpers for making lists of blocks
        pass
