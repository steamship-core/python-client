import logging

import requests

from steamship import Block, SteamshipError
from steamship.experimental.transports.transport import Transport

API_BASE = "https://api.telegram.org/bot"


class TelegramTransport(Transport):
    """Experimental base class to encapsulate a Telegram communication channel."""

    api_root: str

    def __init__(self, bot_token: str):
        self.api_root = f"{API_BASE}{bot_token}"

    def _instance_init(self, *args, **kwargs):
        if "webhook_url" not in kwargs:
            raise SteamshipError(
                message="Please provide the `webhook_url` method in the TelegramTransport instance_init kwargs"
            )

        webhook_url = kwargs["webhook_url"]

        response = requests.get(
            f"{self.api_root}/setWebhook",
            params={"url": webhook_url, "allowed_updates": ["message"]},
        )
        if not response.ok:
            raise SteamshipError(
                f"Could not set webhook for bot. Webhook URL was {webhook_url}. Telegram response message: {response.text}"
            )

    def _send(self, blocks: [Block], chat_id: str):
        """Send a response to the Telegram chat."""
        for block in blocks:
            if block.text:
                params = {"chat_id": int(chat_id), "text": block.text}
                requests.get(f"{self.api_root}/sendMessage", params=params)
            else:
                logging.error("Unable to support sending a block with no text.")

    def _info(self) -> dict:
        """Fetches info about this bot."""
        resp = requests.get(f"{self.api_root}/getMe").json()
        logging.info(f"/info: {resp}")
        return {"telegram": resp.get("result")}
