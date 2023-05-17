from abc import ABC, abstractmethod
from typing import Any, List, Union

from pydantic import BaseModel

from steamship import Block, Task
from steamship.agents.context import AgentContext


class Tool(BaseModel, ABC):
    # Working thinking: we don't yet have formalization about whether
    # this is a class-level name, isntance-level name, or
    # instance+context-level name.
    # thought(doug): this should be the planner-facing name (LLM-friendly?)
    name: str

    # Advice, but not hard-enforced:
    # This contains the description, inputs, and outputs.
    ai_description: str
    human_description: str  # Human readable string for logging

    @abstractmethod
    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        raise NotImplementedError()

    # This gets called later if you return Task[Any] from run
    def post_process(self, async_task: Task[Any]) -> List[Block]:
        # nice helpers for making lists of blocks
        pass
