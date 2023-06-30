from typing import Any, Callable, Dict, List

from steamship import Block, Steamship, Tag
from steamship.agents.schema.action import Action

Metadata = Dict[str, Any]
EmitFunc = Callable[[List[Block], Metadata], None]


class AgentContext:
    """AgentContext contains all relevant information about a particular execution of an Agent. It is used by the
    AgentService to manage execution history as well as store/retrieve information and metadata that will be used
    in the process of an agent execution.
    """

    # A steamship-assigned ID for this memory object
    @property
    def id(self) -> str:
        return self.chat_history.file.id

    metadata: Metadata
    """Allows storage of arbitrary information that may be useful for agents and tools."""

    client: Steamship
    """Provides workspace-specific utilities for the agents and tools."""

    chat_history: "ChatHistory"  # noqa: F821
    """Record of user-package messages. It records user submitted queries/prompts and the final
    agent-driven answer sent in response to those queries/prompts. It does NOT record any chat
    history related to agent execution and action selection."""

    completed_steps: List[Action]
    """Record of agent-selected Actions and their outputs. This provides an ordered look at the
    execution sequence for this context."""

    # todo: in the future, this could be a set of callbacks like onError, onComplete, ...
    emit_funcs: List[EmitFunc]
    """Called when an agent execution has completed. These provide a way for the AgentService
    to return the result of an agent execution to the package that requested the agent execution."""

    def __init__(self):
        self.metadata = {}
        self.completed_steps = []
        self.emit_funcs = []

    @staticmethod
    def get_or_create(
        client: Steamship,
        context_keys: Dict[str, str],
        tags: List[Tag] = None,
        searchable: bool = True,
    ):
        from steamship.agents.schema.chathistory import ChatHistory

        history = ChatHistory.get_or_create(client, context_keys, tags, searchable=searchable)
        context = AgentContext()
        context.chat_history = history
        context.client = client
        return context
