from typing import Dict, Any, List, Optional

from pydantic import BaseModel

from steamship import Steamship
from steamship.experimental.transports.chat import ChatMessage


class ChatHistory(BaseModel):
    chat_id: str = ""  # chat history is scoped by a chat_id. chat_id is unique across user_id's
    messages: List[ChatMessage] = []  # Represents a database that can select & sort messages

    def get_history(self, context, k: Optional[int] = None):
        return [message.text for message in self.messages][-k:]

    def add_user_message(self, message: str):
        self.messages.append(ChatMessage(text=f"user: {message}", who="user"))

    def add_ai_message(self, message: str):
        self.messages.append(ChatMessage(text=f"AI: {message}", who="AI"))

    def clear(self):
        self.messages = []


class AgentContext(BaseModel):
    client: Steamship
    chat_history: Optional[ChatHistory] = ChatHistory()
    tracing: Optional[Dict[str, Any]] = []
    scratchpad: Optional[List[str]] = []

    def emit(self, messages: List[ChatMessage]):
        """Function to send a message to one or more comm channels"""
        for message in messages:
            print(message.text)

    @property
    def last_message(self) -> ChatMessage:
        return self.chat_history.messages[-1]

    class Config:
        arbitrary_types_allowed = True
