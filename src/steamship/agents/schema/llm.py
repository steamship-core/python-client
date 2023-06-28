from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic.main import BaseModel

from steamship import Block
from steamship.agents.schema.tool import Tool


class LLM(BaseModel, ABC):
    """LLM wraps large language model-based backends.

    They may be used with LLMAgents in Action selection, or for direct prompt completion."""

    @abstractmethod
    def complete(self, prompt: str, stop: Optional[str] = None) -> List[Block]:
        """Completes the provided prompt, stopping when the stop sequeunce is found."""
        pass


# TODO(dougreid): should LLM and ConversationalLLM share a common parent?
class ConversationalLLM(BaseModel, ABC):
    """ConversationalLLM wraps large language model-based backends that use a chat completion style interation.

    They may be used with LLMAgents in Action selection, or for direct prompt completion."""

    @abstractmethod
    def converse(self, messages: List[Block], tools: Optional[List[Tool]]) -> List[Block]:
        """Sends the set of messages to the LLM, returning the next part of the conversation"""
        pass
