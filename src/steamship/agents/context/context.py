from abc import ABC
from typing import Any, Callable, Dict, List, Optional, Tuple

from pydantic.main import BaseModel

from steamship import Block, PluginInstance, Steamship, Tag, Task
from steamship.agents.context.chathistory import ChatHistory


class BaseTool(BaseModel, ABC):
    pass


class ToolBinding(BaseModel):
    tool: BaseTool
    inputs: List[Block]


ToolInputs = List[Block]
ToolOutputs = List[Block]
AgentStep = Tuple[ToolBinding, ToolOutputs]
AgentSteps = List[AgentStep]
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

    # A steamship-assigned ID for this context object
    @property
    def id(self) -> str:
        return self.chat_history.file.id

    metadata: Metadata = {}

    client: Steamship

    # User<->Package chat history (NOT Agent<-->Tool history)
    # NB: This is distinct from any sort of history related to agent execution
    # Primarily used to ferry prompts into agent executions AND
    # to allow for some sort of referential lookup of context as input to the agent
    chat_history: ChatHistory

    # Provides the overall goal of the agent
    @property
    def initial_prompt(self) -> Optional[Block]:
        return self.chat_history.initial_system_prompt

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
        Tuple[Any, Task]
    ] = []  # todo: should this be a map from task_id -> ToolBinding?
    # TODO: Any here should be Action, but I can't make it un-circular

    # this, I think(?), is not serializable, and must be set in some sort of context init bit
    # of whatever is doing the work.
    # in the future, this could be a set of callbacks, more broken out (onError, onComplete, ...)
    emit_funcs: List[EmitFunc] = []

    def get_llm(self) -> PluginInstance:
        # This may be something we wish to eventually provide application-level settings for.
        # E.g. the agent has a set_default_llm method that is available and supported in the UI.
        return self.client.use_plugin("gpt-4", config={"model": "gpt-3.5-turbo"})

    @staticmethod
    def get_or_create(
        client: Steamship,
        context_keys: Dict[str, str],
        tags: List[Tag] = None,
    ) -> "AgentContext":
        history = ChatHistory.get_or_create(client, context_keys, tags)
        context = AgentContext()
        context.chat_history = history
        context.client = client
        return context
