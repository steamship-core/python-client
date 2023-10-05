from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel
from pydantic.fields import Field

from steamship import Block
from steamship.agents.schema.action import Action
from steamship.agents.schema.context import AgentContext
from steamship.agents.schema.llm import LLM, ChatLLM
from steamship.agents.schema.message_selectors import MessageSelector, NoMessages
from steamship.agents.schema.output_parser import OutputParser
from steamship.agents.schema.tool import Tool
from steamship.data.tags.tag_constants import RoleTag, TagKind
from steamship.data.tags.tag_utils import get_tag


class Agent(BaseModel, ABC):
    """Agent is responsible for choosing the next action to take for an AgentService.

    It uses the provided context, and a set of Tools, to decide on an action that will
    be executed by the AgentService.
    """

    tools: List[Tool]
    """Tools that can be used by the Agent in selecting the next Action."""

    message_selector: MessageSelector = Field(default=NoMessages())
    """Selector of messages from ChatHistory. Used for conversation memory retrieval."""

    def default_system_message(self) -> Optional[str]:
        """The default system message used by Agents to drive LLM instruction.

        Non Chat-based Agents should always return None. Chat-based Agents should override
        this method to provide a default prompt.
        """
        return None

    @abstractmethod
    def next_action(self, context: AgentContext) -> Action:
        pass

    def record_action_run(self, action: Action, context: AgentContext):
        # TODO(dougreid): should this method (or just bit) actually be on AgentContext?
        context.completed_steps.append(action)


class LLMAgent(Agent):
    """LLMAgents choose next actions for an AgentService based on interactions with an LLM."""

    llm: LLM
    """The LLM to use for action selection."""

    output_parser: OutputParser
    """Utility responsible for converting LLM output into Actions"""

    @abstractmethod
    def next_action(self, context: AgentContext) -> Action:
        pass

    @staticmethod
    def messages_to_prompt_history(messages: List[Block]) -> str:
        as_strings = []
        for block in messages:
            role = block.chat_role
            # Internal Status Messages are not considered part of **prompt** history.
            # Their inclusion could lead to problematic LLM behavior, etc.
            # As such are explicitly skipped here:
            # - DON'T RETURN STATUS MESSAGES
            # - DON'T RETURN FUNCTION or FUNCTION_SELECTION MESSAGES
            if role == RoleTag.USER:
                as_strings.append(f"User: {block.text}")
            elif role == RoleTag.ASSISTANT and (
                get_tag(block.tags, TagKind.FUNCTION_SELECTION) is None
            ):
                as_strings.append(f"Assistant: {block.text}")
            elif role == RoleTag.SYSTEM:
                as_strings.append(f"System: {block.text}")
        return "\n".join(as_strings)


class ChatAgent(Agent, ABC):
    """ChatAgents choose next actions for an AgentService based on chat-based interactions with an LLM."""

    llm: ChatLLM

    output_parser: OutputParser
    """Utility responsible for converting LLM output into Actions"""
