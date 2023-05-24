from abc import ABC, abstractmethod
from typing import List, Optional

from steamship import Block
from steamship.experimental.transports.steamship_widget import SteamshipWidgetTransport
from steamship.invocable import PackageService, post


def response_for_exception(e: Optional[Exception], chat_id: Optional[str] = None) -> Block:
    return_text = f"An error happened while creating a response: {e}"
    if e is None:
        return_text = "An unknown error happened. Please reach out to support@steamship.com or on our discord at https://steamship.com/discord"

    if "usage limit" in f"{e}":
        return_text = "You have reached the introductory limit of Steamship. Visit https://steamship.com/account/plan to sign up for a plan."

    result = Block(text=return_text)
    result.set_chat_id(chat_id)
    return result


class SteamshipWidgetBot(PackageService, ABC):
    steamship_widget_transport: SteamshipWidgetTransport

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.steamship_widget_transport = SteamshipWidgetTransport(client=self.client)

    @abstractmethod
    def create_response(self, incoming_message: Block) -> Optional[List[Block]]:
        raise NotImplementedError

    @post("answer", public=True)
    def answer(self, **payload) -> List[Block]:
        """Endpoint that implements the contract for Steamship embeddable chat widgets. This is a PUBLIC endpoint since these webhooks do not pass a token."""
        incoming_message = self.steamship_widget_transport.parse_inbound(payload)
        try:
            response = self.create_response(incoming_message)
        except Exception as e:
            response = response_for_exception(e, chat_id=incoming_message.chat_id)

        # We don't call self.steamship_widget_transport.send because the result is the return value
        return response
