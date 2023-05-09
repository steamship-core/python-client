import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Type

from pydantic import Field

from steamship import SteamshipError
from steamship.experimental.package_starters.web_bot import WebBot
from steamship.experimental.transports import TelegramTransport
from steamship.experimental.transports.chat import ChatMessage
from steamship.invocable import Config, InvocableResponse, post


class TelegramBotConfig(Config):
    bot_token: str = Field(description="The secret token for your Telegram bot")


class TelegramBot(WebBot, ABC):
    config: TelegramBotConfig
    telegram_transport: TelegramTransport

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class."""
        return TelegramBotConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def instance_init(self):
        """This instance init method is called automatically when an instance of this package is created. It registers the URL of the instance as the Telegram webhook for messages."""
        try:
            webhook_url = self.context.invocable_url + "respond"
            self.telegram_transport = TelegramTransport(bot_token=self.config.bot_token)
            self.telegram_transport.instance_init(webhook_url=webhook_url)
        except Exception as ex:
            logging.error(ex)

    @post("telegram_respond", public=True)
    def telegram_respond(self, **kwargs) -> InvocableResponse:
        """Respond to a Telegram message.
        This is a PUBLIC endpoint since Telegram cannot pass a Bearer token."""
        chat_id = None
        try:
            input_message = self.telegram_transport.parse_inbound(payload=kwargs["message"])

            if not input_message.text:
                # If we do nothing, make sure we return ok
                return InvocableResponse(string="OK")
            else:
                response: List[ChatMessage] = self.respond(message_text=input_message.text,
                                                           chat_id=input_message.get_chat_id(),
                                                           message_id=input_message.get_message_id())


        except SteamshipError as e:
            response = [
                ChatMessage(
                    client=self.client,
                    chat_id=kwargs.get("chat_session_id"),
                    text=self.response_for_exception(e),
                )
            ]

        self.telegram_transport.send(response)

    @abstractmethod
    def respond(
            self, message_text: str, chat_id: int, message_id: int
    ) -> Optional[List[ChatMessage]]:
        pass

    @post("webhook_info")
    def webhook_info(self) -> dict:
        return self.telegram_transport.webhook_info()

    @post("info")
    def info(self) -> dict:
        """Endpoint returning information about this bot."""
        return self.telegram_transport.info()

    @post("disconnect_webhook")
    def disconnect_webhook(self) -> InvocableResponse[str]:
        self.telegram_transport.instance_deinit()
        return InvocableResponse(data="OK")
