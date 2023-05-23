from typing import List, Optional

from steamship import Block
from steamship.agents.service.agent_service import AgentService
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship.experimental.transports.chat import ChatMessage


class MultiInheritanceBot(AgentService, TelegramBot):
    def create_response(self, incoming_message: ChatMessage) -> Optional[List[ChatMessage]]:
        return [ChatMessage.from_block(Block(text="Yo"))]
