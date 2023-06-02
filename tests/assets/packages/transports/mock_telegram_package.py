from typing import List

from steamship import File, Tag
from steamship.invocable import PackageService, get


class MockTelegram(PackageService):
    WEBHOOK_TAG = "webhook"
    TEXT_MESSAGE_TAG = "text_message"
    CHAT_ID_KEY = "chat_id"

    @get("setWebhook", public=True)
    def set_webhook(self, url: str, allowed_updates: List[str], drop_pending_updates: bool) -> str:
        File.create(self.client, blocks=[], tags=[Tag(kind=self.WEBHOOK_TAG, name=url)])
        return "OK"

    @get("sendMessage", public=True)
    def send_message(self, chat_id: int, text: str):
        File.create(
            self.client,
            blocks=[],
            tags=[Tag(kind=self.TEXT_MESSAGE_TAG, name=text, value={self.CHAT_ID_KEY: chat_id})],
        )
        return "OK"

    # TODO
    # @post("sendPhoto", public=True)
    # @post("sendAudio", public=True)
    # @post("sendVideo", public=True)
