import logging
import tempfile
from typing import Optional

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
        logging.info(f"Setting Telegram webhook URL: {webhook_url}")
        logging.info(f"Post is to {self.api_root}/setWebhook")

        response = requests.get(
            f"{self.api_root}/setWebhook",
            params={
                "url": webhook_url,
                "allowed_updates": ["message"],
                "drop_pending_updates": True,
            },
        )

        if not response.ok:
            raise SteamshipError(
                f"Could not set webhook for bot. Webhook URL was {webhook_url}. Telegram response message: {response.text}"
            )

    def _instance_deinit(self, *args, **kwargs):
        """Unsubscribe from Telegram updates."""
        requests.get(f"{self.api_root}/deleteWebhook")

    def _send(self, blocks: [Block]):
        """Send a response to the Telegram chat."""
        for block in blocks:
            chat_id = block.chat_id
            if block.is_text() or block.text:
                params = {"chat_id": int(chat_id), "text": block.text}
                requests.get(f"{self.api_root}/sendMessage", params=params)
            elif block.is_image() or block.is_audio() or block.is_video():
                if block.is_image():
                    suffix = "sendPhoto"
                    key = "photo"
                elif block.is_audio():
                    suffix = "sendAudio"
                    key = "audio"
                elif block.is_video():
                    suffix = "sendVideo"
                    key = "video"

                _bytes = block.raw()
                with tempfile.TemporaryFile(mode="r+b") as temp_file:
                    temp_file.write(_bytes)
                    temp_file.seek(0)
                    resp = requests.post(
                        url=f"{self.api_root}/{suffix}?chat_id={chat_id}",
                        files={key: temp_file},
                    )
                    if resp.status_code != 200:
                        logging.error(f"Error sending message: {resp.text} [{resp.status_code}]")
                        raise SteamshipError(
                            f"Message not sent to chat {chat_id} successfully: {resp.text}"
                        )
            else:
                logging.error(
                    f"Telegram transport unable to send a block of MimeType {block.mime_type}"
                )

    def _info(self) -> dict:
        """Fetches info about this bot."""
        resp = requests.get(f"{self.api_root}/getMe").json()
        logging.info(f"/info: {resp}")
        return {"telegram": resp.get("result")}

    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        """Parses an inbound Telegram message."""

        chat = payload.get("chat")
        if chat is None:
            raise SteamshipError(f"No `chat` found in Telegram message: {payload}")

        chat_id = chat.get("id")
        if chat_id is None:
            raise SteamshipError(f"No 'chat_id' found in Telegram message: {payload}")

        if not isinstance(chat_id, int):
            raise SteamshipError(
                f"Bad 'chat_id' found in Telegram message: ({chat_id}). Should have been an int."
            )

        message_id = payload.get("message_id")
        if message_id is None:
            raise SteamshipError(f"No 'message_id' found in Telegram message: {payload}")

        if not isinstance(message_id, int):
            raise SteamshipError(
                f"Bad 'message_id' found in Telegram message: ({message_id}). Should have been an int"
            )

        # Some incoming messages (like the group join message) don't have message text.
        # Rather than throw an error, we just don't return a Block.
        message_text = payload.get("text")
        if message_text is not None:
            result = Block(text=message_text)
            result.set_chat_id(str(chat_id))
            result.set_message_id(str(message_id))
            return result
        else:
            return None
