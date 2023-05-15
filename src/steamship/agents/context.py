from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel

from steamship import Block
from steamship.data.tags.tag_constants import RoleTag


class AgentContext(BaseModel, ABC):
    # The Context of an Agent comprises:
    #  * The chat history of the agent with the user,
    #  * Explicitly stored long-term data for the user:
    #    * Fetchable by key, if one is provided
    #    * Searchable
    # Context is specific to a single user, for now.
    # This version makes the concept of "Memory" just part of the implementation of context;
    #   if we don't like this we can split it out

    @abstractmethod
    @staticmethod
    def get_or_create_context(user_id: str) -> "AgentContext":
        """Get or create a new context for a particular end-user"""
        pass

    # Chat history (short term memory)
    # This could be stored in a File object

    @abstractmethod
    def conversation_history(self, max_tokens: Optional[int] = None) -> List[Block]:
        """Get the history of the conversation"""
        pass

    @abstractmethod
    def add_message(self, message: Block, role: RoleTag):
        """Add a bit of conversation to the history."""
        pass

    def add_user_message(self, message: Block):
        self.add_message(message, RoleTag.USER)

    def add_system_message(self, message: Block):
        self.add_message(message, RoleTag.SYSTEM)

    def add_agent_message(self, message: Block):
        self.add_message(message, RoleTag.ASSISTANT)

    # Long term memory
    # This could be stored in the combination of a File object and the vector store.

    @abstractmethod
    def add_memory(self, value: Block, key: Optional[str] = None):
        """Store something we want to remember. Optional key allows retrieval by key later."""
        pass

    @abstractmethod
    def get_memory_by_key(self, key: str) -> Optional[Block]:
        """Method queries existing long-term memory by key. Returns None if there are no memories with that key."""
        pass

    @abstractmethod
    def search_memory(self, query: Block) -> Optional[Block]:
        """Method searches existing long-term memory. Interface takes block and not text to allow for multimodal search later."""
        pass
