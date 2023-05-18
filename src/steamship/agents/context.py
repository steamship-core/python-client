from typing import Dict, Any, List, Optional

from pydantic import BaseModel

from steamship import Steamship
from steamship.experimental.transports.chat import ChatMessage


class ChatHistory(BaseModel):
    chat_id: str = ""  # chat history is scoped by a chat_id. chat_id is unique across user_id's
    messages: List[str] = []  # Represents a database that can select & sort messages

    def get_history(self, message: ChatMessage, context):
        return self.messages

    def add_user_message(self, message: ChatMessage):
        self.messages.append(f"user: {message}")

    def add_ai_message(self, message: ChatMessage):
        self.messages.append(f"AI: {message}")

    def clear(self):
        self.messages = []


class AgentContext(BaseModel):
    client: Steamship
    chat_history: Optional[ChatHistory] = ChatHistory()
    tracing: Optional[Dict[str, Any]] = []
    scratchpad: Optional[List[str]] = []
    new_message: str = ""

    def emit(self, messages: List[ChatMessage]):
        """Function to send a message to one or more comm channels"""
        for message in messages:
            print(message.text)

    class Config:
        arbitrary_types_allowed = True
