import logging
import uuid
from typing import Any, Callable, Dict, List, Optional

from steamship import Block, Steamship, Tag
from steamship.agents.logging import StreamingOpts
from steamship.agents.schema.action import Action
from steamship.agents.schema.cache import ActionCache, LLMCache

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

    action_cache: Optional[ActionCache]
    """Caches all interations with Tools within a Context. This provides a way to avoid duplicated
    calls to Tools when within the same context."""

    llm_cache: Optional[LLMCache]
    """Caches all interations with LLMs within a Context. This provides a way to avoid duplicated
    calls to LLMs when within the same context."""

    request_id: str
    """Identifier for the current request being handled by this context."""

    def __init__(self, request_id: str, streaming_opts: Optional[StreamingOpts] = None):
        self.metadata = {}
        self.completed_steps = []
        self.emit_funcs = []
        self.request_id = request_id  # TODO: protect this?
        if streaming_opts is not None:
            self._streaming_opts = streaming_opts
        else:
            self._streaming_opts = StreamingOpts()

    @staticmethod
    def get_or_create(
        client: Steamship,
        context_keys: Dict[str, str],
        tags: List[Tag] = None,
        searchable: bool = True,
        use_llm_cache: Optional[bool] = False,
        use_action_cache: Optional[bool] = False,
        streaming_opts: Optional[StreamingOpts] = None,
        request_id: Optional[str] = None,
    ):
        from steamship.agents.schema.chathistory import ChatHistory

        if streaming_opts is None:
            streaming_opts = StreamingOpts()

        if request_id is None:
            request_id = str(uuid.uuid4())

        history = ChatHistory.get_or_create(client, context_keys, tags, searchable=searchable)
        context = AgentContext(streaming_opts=streaming_opts, request_id=request_id)
        context.chat_history = history
        context.client = client

        if use_action_cache:
            context.action_cache = ActionCache.get_or_create(
                client=client, context_keys=context_keys
            )
        else:
            context.action_cache = None

        if use_llm_cache:
            context.llm_cache = LLMCache.get_or_create(client=client, context_keys=context_keys)
        else:
            context.llm_cache = None

        return context

    def __enter__(self):
        from steamship.agents.schema.chathistory import ChatHistoryLoggingHandler

        if self._streaming_opts.stream_intermediate_events:
            self._chat_history_logger = ChatHistoryLoggingHandler(
                chat_history=self.chat_history,
                streaming_opts=self._streaming_opts,
                request_id=self.request_id,
            )
            logger = logging.getLogger()
            logger.addHandler(self._chat_history_logger)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._chat_history_logger:
            logger = logging.getLogger()
            logger.removeHandler(self._chat_history_logger)
            self._chat_history_logger = None

        # Here we append a final request complete block, which will have no text, but hold a special tag
        # NOTE: This **MUST** happen as the absolute last thing in the AgentService run. If chat history
        # is updated **outside** of `run_agent`, then this will signal a request completion **before** it happens.
        if self._streaming_opts.include_agent_messages:
            self.chat_history.append_request_complete_message(self.request_id)
