import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Type

import requests
from pydantic import Field

from steamship import SteamshipError
from steamship.experimental.package_starters.web_bot import WebBot
from steamship.invocable import Config, InvocableResponse, post


class TelegramBotConfig(Config):
    bot_token: str = Field(description="The secret token for your Telegram bot")


class TelegramBot(WebBot, ABC):

    config: TelegramBotConfig

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class."""
        return TelegramBotConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_root = f"https://api.telegram.org/bot{self.config.bot_token}"

    def instance_init(self):
        """This instance init method is called automatically when an instance of this package is created. It registers the URL of the instance as the Telegram webhook for messages."""
        webhook_url = self.context.invocable_url + "respond"
        response = requests.get(
            f"{self.api_root}/setWebhook",
            params={"url": webhook_url, "allowed_updates": ["message"]},
        )
        if not response.ok:
            raise SteamshipError(
                f"Could not set webhook for bot. Is your Telegram token valid? Webhook URL was {webhook_url}. Telegram response message: {response.text}"
            )
        logging.info(f"Initialized webhook with URL {webhook_url}")

    @abstractmethod
    def respond_to_text(
        self, message_text: str, chat_id: int, message_id: int, update_kwargs: dict
    ) -> Optional[str]:
        pass

    def respond_to_text_with_sources(
        self, message_text: str, chat_id: str
    ) -> (Optional[str], Optional[List[str]]):
        if not chat_id:
            chat_id = "0"
        try:
            chat_session_numeric_id = int(chat_id)
        except ValueError:
            chat_session_numeric_id = 0

        message_id = 0
        return self.respond_to_text(message_text, chat_session_numeric_id, message_id, {}), []

    @post("respond", public=True)
    def respond(self, update_id: int, **kwargs) -> InvocableResponse[str]:
        """Endpoint implementing the Telegram WebHook contract. This is a PUBLIC endpoint since Telegram cannot pass a Bearer token."""
        chat_id = None
        try:
            message = kwargs.get("message", None)
            message_text = (message or {}).get("text", "")

            if (not message_text) or len(message_text) == 0:
                # If we do nothing, make sure we return ok
                return InvocableResponse(string="OK")

            else:
                chat_id = message["chat"]["id"]
                message_id = message["message_id"]

                # TODO: must reject things not from the package

                try:
                    response = self.respond_to_text(message_text, chat_id, message_id, kwargs)
                except SteamshipError as e:
                    response = self.response_for_exception(e)
                if response is not None:
                    self.send_response(chat_id, response)

                return InvocableResponse(string="OK")
        except Exception as e:
            response = self.response_for_exception(e)
            if chat_id is not None:
                self.send_response(chat_id, response)
            return InvocableResponse(string="OK")

    def send_response(self, chat_id: int, text: str):
        """Send a response to the chat in Telegram"""
        reply_params = {
            "chat_id": chat_id,
            "text": text,
        }
        requests.get(self.api_root + "/sendMessage", params=reply_params)

    @post("webhook_info")
    def webhook_info(self) -> dict:
        return requests.get(self.api_root + "/getWebhookInfo").json()

    @post("info")
    def info(self) -> dict:
        """Endpoint returning information about this bot."""
        resp = requests.get(self.api_root + "/getMe").json()
        logging.info(f"/info: {resp}")
        return {"telegram": resp.get("result")}

    @post("disconnect_webhook")
    def disconnect_webhook(self) -> InvocableResponse[str]:
        response = requests.get(f"{self.api_root}/setWebhook", params={"url": ""})
        if not response.ok:
            raise SteamshipError(
                f"Could not disconnect webhook for bot. Telegram response message: {response.text}"
            )
        logging.info("Disconnected webhook.")
        return InvocableResponse(data="OK")
