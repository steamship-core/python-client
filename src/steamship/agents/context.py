from typing import Dict, Any, List, Optional

from pydantic import BaseModel

from steamship import Steamship
from steamship.experimental.transports.chat import ChatMessage


class ChatHistory:
    chat_id: str = ""
    messages: List[str] = []

    def get_history(self):
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

    class Config:
        arbitrary_types_allowed = True
