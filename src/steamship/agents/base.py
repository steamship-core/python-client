from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from steamship import Block, Task
from steamship.agents.context.context import AgentContext


class Action:
    pass  # Circular dependency


ToolInputs = List[Block]
ToolOutputs = List[Block]
AgentSteps = List[Action]
Metadata = Dict[str, Any]
EmitFunc = Callable[[ToolOutputs, Metadata], None]


class BaseTool(BaseModel, ABC):
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
    def post_process(self, async_task: Task, context: AgentContext) -> List[Block]:
        # nice helpers for making lists of blocks
        pass


class Action(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    tool: BaseTool  # Tools are retrieved via their name
    tool_input: List[Block]  # Tools always get strings as input
    context: AgentContext
    tool_output: Optional[ToolOutputs] = []


class FinishAction(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    output: Any  # Output can be anything as long as it's JSON serializable
    context: AgentContext


class LLM(BaseModel, ABC):
    @abstractmethod
    def complete(self, prompt: str, stop: str) -> List[Block]:
        pass
