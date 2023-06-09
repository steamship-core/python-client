from typing import List

from steamship import File, Tag
from steamship.invocable import PackageService, get, post


class MockTelegram(PackageService):
    WEBHOOK_TAG = "webhook"
    TEXT_MESSAGE_TAG = "text_message"
    CHAT_ID_KEY = "chat_id"
    PHOTO_MESSAGE_TAG = "photo_message"
    PHOTO_KEY = "photo"
    AUDIO_MESSAGE_TAG = "audio_message"
    AUDIO_KEY = "audio"
    VIDEO_MESSAGE_TAG = "video_message"
    VIDEO_KEY = "video"

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

    @post("sendPhoto", public=True)
    def send_photo(
        self, chat_id: int, photo: str
    ):  # realize str is wrong here, but seems to be what I get from the file upload to our server.
        File.create(
            self.client,
            blocks=[],
            tags=[
                Tag(
                    kind=self.PHOTO_MESSAGE_TAG,
                    value={self.CHAT_ID_KEY: chat_id, self.PHOTO_KEY: photo},
                )
            ],
        )
        return "OK"

    @post("sendAudio", public=True)
    def send_audio(
        self, chat_id: int, audio: str
    ):  # realize str is wrong here, but seems to be what I get from the file upload to our server.
        File.create(
            self.client,
            blocks=[],
            tags=[
                Tag(
                    kind=self.AUDIO_MESSAGE_TAG,
                    value={self.CHAT_ID_KEY: chat_id, self.AUDIO_KEY: audio},
                )
            ],
        )
        return "OK"

    @post("sendVideo", public=True)
    def send_video(
        self, chat_id: int, video: str
    ):  # realize str is wrong here, but seems to be what I get from the file upload to our server.
        File.create(
            self.client,
            blocks=[],
            tags=[
                Tag(
                    kind=self.VIDEO_MESSAGE_TAG,
                    value={self.CHAT_ID_KEY: chat_id, self.VIDEO_KEY: video},
                )
            ],
        )
        return "OK"
