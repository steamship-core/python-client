from typing import List, Optional

from steamship import Block
from steamship.agents.service.agent_service import AgentService
from steamship.experimental.package_starters.telegram_bot import TelegramBot


class MultiInheritanceBot(AgentService, TelegramBot):
    def create_response(self, incoming_message: Block) -> Optional[List[Block]]:
        return [Block(text="Yo")]
