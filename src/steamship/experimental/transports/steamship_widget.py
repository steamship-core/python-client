import uuid
from typing import Optional

from steamship import Block, SteamshipError
from steamship.experimental.transports.transport import Transport

API_BASE = "https://api.telegram.org/bot"


class SteamshipWidgetTransport(Transport):
    """Experimental base class to encapsulate a Steamship web widget communication channel."""

    def _instance_init(self, *args, **kwargs):
        pass

    def _instance_deinit(self, *args, **kwargs):
        """Unsubscribe from updates."""
        pass

    def _send(self, blocks: [Block]):
        """Send a response to the client.

        TODO: Since this isn't a push, but rather an API return, we need to figure out how to model this.
        """
        pass

    def _info(self) -> dict:
        """Fetches info about this bot."""
        return {}

    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        """Parses an inbound Steamship widget message."""

        message_text = payload.get("question")
        if message_text is None:
            raise SteamshipError(f"No 'question' found in Steamship widget message: {payload}")

        chat_id = payload.get("chat_session_id", "default")

        message_id = str(uuid.uuid4())

        result = Block(text=message_text)
        result.set_chat_id(str(chat_id))
        result.set_message_id(str(message_id))
        return result
