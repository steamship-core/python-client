from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from steamship import Block
from steamship.agents.schema.action import Action
from steamship.agents.schema.context import AgentContext
from steamship.agents.schema.llm import LLM, ChatLLM
from steamship.agents.schema.message_selectors import MessageSelector, NoMessages
from steamship.agents.schema.output_parser import OutputParser
from steamship.agents.schema.tool import Tool
from steamship.data.tags.tag_constants import RoleTag


class Agent(BaseModel, ABC):
    """Agent is responsible for choosing the next action to take for an AgentService.

    It uses the provided context, and a set of Tools, to decide on an action that will
    be executed by the AgentService.
    """

    tools: List[Tool]
    """Tools that can be used by the Agent in selecting the next Action."""

    message_selector: MessageSelector = NoMessages()
    """Selector of messages from ChatHistory. Used for conversation memory retrieval."""

    @abstractmethod
    def next_action(self, context: AgentContext) -> Action:
        pass


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
            if role == RoleTag.USER:
                as_strings.append(f"User: {block.text}")
            elif role == RoleTag.ASSISTANT:
                as_strings.append(f"Assistant: {block.text}")
            elif role == RoleTag.SYSTEM:
                as_strings.append(f"System: {block.text}")
            elif role == RoleTag.AGENT:
                as_strings.append(f"Agent: {block.text}")
            elif role == RoleTag.FUNCTION:
                as_strings.append(f"Function: {block.text}")
        return "\n".join(as_strings)


class ChatAgent(Agent, ABC):
    """ChatAgents choose next actions for an AgentService based on chat-based interactions with an LLM."""

    llm: ChatLLM

    output_parser: OutputParser
    """Utility responsible for converting LLM output into Actions"""
