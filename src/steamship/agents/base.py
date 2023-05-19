from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from steamship import Block, PluginInstance, Steamship, Task


class Action:
    pass  # Circular dependency


ToolInputs = List[Block]
ToolOutputs = List[Block]
AgentSteps = List[Action]
Metadata = Dict[str, Any]
EmitFunc = Callable[[ToolOutputs, Metadata], None]


class AgentContext:
    # AgentContext is passed as a parameter for any `run_agent()` call on the `AgentService`
    # as well as any `Tool.run()` call. It provides access to arbitrary metadata about the
    # context of any agent invocation, as well as anything relevant to the `AgentService`
    # instance etc.
    #
    # It also provides access to two-distinct types of "history" or "memory":
    # (1) user <-> package interactions
    # (2) agent and tool interactions
    #
    # It is meant to be persisted (via a KeyValueStore or otherwise) to allow for
    # restarts, interruptions, etc.

    # NB: I've forgone the go-style contexts as structs with key-values here for now
    # i still believe there is value there, but i didn't want that to interfere with
    # readability too much when just trying to string together the concepts.
    id: str
    metadata: Metadata = {}

    # maybe needed?
    client: Steamship

    # User<->Package chat history (NOT Agent<-->Tool history)
    # NB: This is distinct from any sort of history related to agent execution
    # Primarily used to ferry prompts into agent executions AND
    # to allow for some sort of referential lookup of context as input to the agent
    # chat_history: ChatFile

    # Provides the overall goal of the agent
    # Maybe this can be derived from the chat_history, or whatever, but this
    # is a simplifying assumption.
    initial_prompt: List[Block]

    # instead of saving the execution history via File as text, this chooses to represent
    # state as objects. this may not be what we want. This could also be:
    # agent_history: ChatFile (with tags on blocks to represent state of Tool execution)
    # i need to think about that a bit more.
    #
    # for each of these bits, we probably need to save only IDs, and rehydrate properly;
    # likely requires an override of `dict()` and `parse_obj()`
    completed_steps: AgentSteps = []

    # This supports parallel tool execution. But I think that should
    # be a future iteration, as it complicates things quite a bit.
    #
    # as above this likely could be "discovered" from `agent_history: ChatFile` and tags
    # dynamically, and be more "Steamship-native". Perhaps in a second pass.
    in_progress: List[
        Tuple[Action, Task]
    ] = []  # todo: should this be a map from task_id -> ToolBinding?

    # this, I think(?), is not serializable, and must be set in some sort of context init bit
    # of whatever is doing the work.
    # in the future, this could be a set of callbacks, more broken out (onError, onComplete, ...)
    emit_funcs: List[EmitFunc] = []

    def get_llm(self) -> PluginInstance:
        # This may be something we wish to eventually provide application-level settings for.
        # E.g. the agent has a set_default_llm method that is available and supported in the UI.
        return self.client.use_plugin("gpt-4", config={"model": "gpt-3.5-turbo"})


class BaseTool(ABC):
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
