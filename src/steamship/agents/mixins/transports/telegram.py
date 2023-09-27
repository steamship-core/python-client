import logging
import tempfile
from typing import Any, Dict, List, Optional

import requests
from pydantic import Field

from steamship import Block, Steamship, SteamshipError
from steamship.agents.mixins.transports.transport import Transport
from steamship.agents.schema import EmitFunc, Metadata
from steamship.agents.service.agent_service import AgentService, build_context_appending_emit_func
from steamship.invocable import Config, InvocableResponse, post
from steamship.utils.kv_store import KeyValueStore

SETTINGS_KVSTORE_KEY = "telegram-transport"


class TelegramTransportConfig(Config):
    bot_token: Optional[str] = Field("", description="The secret token for your Telegram bot")
    api_base: Optional[str] = Field(
        "https://api.telegram.org/bot", description="The root API for Telegram"
    )


class TelegramTransport(Transport):
    """Experimental base class to encapsulate a Telegram communication channel."""

    bot_token: Optional[str] = None
    agent_service: AgentService
    config: TelegramTransportConfig

    def __init__(
        self,
        client: Steamship,
        config: TelegramTransportConfig,
        agent_service: AgentService,
    ):
        super().__init__(client=client)
        self.config = config
        self.agent_service = agent_service
        try:
            self.bot_token = self.get_telegram_access_token() or None
        except BaseException as e:
            logging.warning(e)
            self.bot_token = None

    def instance_init(self):
        if self.get_telegram_access_token():
            try:
                self.telegram_connect_webhook()
            except Exception:  # noqa: S110
                pass

    @post("telegram_connect_webhook")
    def telegram_connect_webhook(self):
        """Register this AgentService with Telegram."""
        webhook_url = self.agent_service.context.invocable_url + "telegram_respond"

        api_root = self.get_api_root()
        if not api_root:
            raise SteamshipError(
                message="Unable to determine Telegram API root -- perhaps your bot token isn't set?"
            )

        logging.info(
            f"Setting Telegram webhook URL: {webhook_url}. Post is to {api_root}/setWebhook"
        )

        response = requests.get(
            f"{api_root}/setWebhook",
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

    @post("telegram_bot_info")
    def telegram_bot_info(self) -> dict:
        api_root = self.get_api_root()
        if not api_root:
            raise SteamshipError(
                message="Unable to fetch Telegram Bot info -- perhaps your bot token isn't set?"
            )

        return requests.get(api_root + "/getMe").json()

    @post("telegram_webhook_info")
    def telegram_webhook_info(self) -> dict:
        api_root = self.get_api_root()
        if not api_root:
            raise SteamshipError(
                message="Unable to fetch Telegram Webhook info -- perhaps your bot token isn't set?"
            )

        return requests.get(api_root + "/getWebhookInfo").json()

    @post("telegram_disconnect_webhook")
    def telegram_disconnect_webhook(self, *args, **kwargs):
        """Unsubscribe from Telegram updates."""
        api_root = self.get_api_root()
        if not api_root:
            raise SteamshipError(
                message="Unable to disconnect from Telegram -- perhaps your bot token isn't set?"
            )

        requests.get(f"{api_root}/deleteWebhook")

    def _send(self, blocks: [Block], metadata: Metadata):
        """Send a response to the Telegram chat."""
        api_root = self.get_api_root()
        if not api_root:
            raise SteamshipError(
                message="Unable to send to Telegram -- perhaps your bot token isn't set?"
            )

        for block in blocks:
            chat_id = block.chat_id
            if block.is_text() or block.text:
                params = {"chat_id": int(chat_id), "text": block.text}
                requests.get(f"{api_root}/sendMessage", params=params)
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
                        url=f"{api_root}/{suffix}?chat_id={chat_id}",
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

    def _get_file(self, file_id: str) -> Dict[str, Any]:
        api_root = self.get_api_root()
        if not api_root:
            raise SteamshipError(
                message="Unable to get Telegram file -- perhaps your bot token isn't set?"
            )

        return requests.get(f"{api_root}/getFile", params={"file_id": file_id}).json()["result"]

    def _get_file_url(self, file_id: str) -> str:
        return f"https://api.telegram.org/file/bot{self.get_telegram_access_token()}/{self._get_file(file_id)['file_path']}"

    def _download_file(self, file_id: str):
        result = requests.get(self._get_file_url(file_id))
        if result.status_code != 200:
            raise Exception("Download file", result)

        return result.content

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

        if video_or_voice := (payload.get("voice") or payload.get("video_note")):
            file_id = video_or_voice.get("file_id")
            file_url = self._get_file_url(file_id)
            block = Block(
                text=payload.get("text"),
                url=file_url,
            )
            block.set_chat_id(str(chat_id))
            block.set_message_id(str(message_id))
            return block

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

    def build_emit_func(self, chat_id: str) -> EmitFunc:
        def new_emit_func(blocks: List[Block], metadata: Metadata):
            for block in blocks:
                block.set_chat_id(chat_id)
            return self.send(blocks, metadata)

        return new_emit_func

    @post("telegram_respond", public=True)
    def telegram_respond(self, **kwargs) -> InvocableResponse[str]:
        """Endpoint implementing the Telegram WebHook contract. This is a PUBLIC endpoint since Telegram cannot pass a Bearer token."""

        # TODO: must reject things not from the package
        message = kwargs.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        try:
            incoming_message = self.parse_inbound(message)
            if incoming_message is not None:
                with self.agent_service.build_default_context(chat_id) as context:
                    context.chat_history.append_user_message(
                        text=incoming_message.text, tags=incoming_message.tags
                    )

                    context.emit_funcs = [
                        self.build_emit_func(chat_id=chat_id),
                        # allow telegram access to blocks on emit (making them public)
                        build_context_appending_emit_func(context=context, make_blocks_public=True),
                    ]

                    self.agent_service.run_agent(self.agent_service.get_default_agent(), context)
            else:
                # Do nothing here; this could be a message we intentionally don't want to respond to (ex. an image or file upload)
                pass
        except Exception as e:
            response = self.response_for_exception(e, chat_id=chat_id)

            if chat_id is not None:
                self.send([response])
        # Even if we do nothing, make sure we return ok
        return InvocableResponse(string="OK")

    @post("set_telegram_access_token")
    def set_telegram_access_token(self, token: str) -> InvocableResponse[str]:
        """Set the telegram access token."""
        existing_token = self.get_telegram_access_token()
        if existing_token:
            try:
                self.telegram_disconnect_webhook()
            except BaseException as e:
                # Note: we don't want to fully fail here, because that would mean that a bot user that had some
                # other error relating to disconnecting would never be able to RE-connect to a new bot.
                logging.error(e)

        kv = KeyValueStore(
            client=self.agent_service.client, store_identifier=self.setting_store_key()
        )
        kv.set("telegram_token", {"token": token})

        # Now attempt to modify the connection in Telegram
        self.bot_token = token
        try:
            self.telegram_connect_webhook()
            return InvocableResponse(string="OK")
        except Exception as e:
            raise SteamshipError(message=f"Could not set Telegram Webhook. Exception: {e}")

    def get_api_root(self) -> Optional[str]:
        """Return the API root"""
        bot_token = self.get_telegram_access_token()
        api_base = self.config.api_base

        # Ensure we have an API Base
        if not api_base:
            raise SteamshipError(message="Missing Telegram API Base")

        # Ensure it ends in a trailing slash
        if api_base[-1] != "/":
            api_base += "/"

        if bot_token:
            if ".steamship.run/" in api_base or ".apps.staging.steamship.com" in api_base:
                # This is a special case for our testing pipeline -- it contains a mock Telegram server.
                return api_base[:-1]
            else:
                return f"{api_base[:-1]}{bot_token}"
        else:
            return None

    def setting_store_key(self):
        return f"{SETTINGS_KVSTORE_KEY}-{self.agent_service.context.invocable_instance_handle}"

    def get_telegram_access_token(self) -> Optional[str]:
        """Return the Telegram Access token, which permits the agent to post to Telegram."""

        # Warning: This can't be an 'is not None' check since the config system uses an empty string to represent None
        if self.bot_token:
            return self.bot_token

        _dynamically_set_token = None
        _fallback_token = None

        # Prefer the dynamically set token if available
        kv = KeyValueStore(
            client=self.agent_service.client, store_identifier=self.setting_store_key()
        )
        v = kv.get("telegram_token")
        if v:
            _dynamically_set_token = v.get("token", None)

        # Fall back on the config-provided one
        if self.config:
            _fallback_token = self.config.bot_token

        _return_token = _dynamically_set_token or _fallback_token

        # Cache it to avoid another KV Store lookup and return
        self.bot_token = _return_token
        return _return_token

    @post("is_telegram_token_set")
    def is_telegram_token_set(self) -> InvocableResponse[bool]:
        """Return whether the Telegram token has been set as a way for a remote UI to check status."""

        # Warning: This can't be an 'is not None' check since the config system uses an empty string to represent None
        if not self.get_telegram_access_token():
            return InvocableResponse(json=False)
        return InvocableResponse(json=True)
