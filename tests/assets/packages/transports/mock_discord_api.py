from typing import Dict, List

from steamship import File, SteamshipError, Tag
from steamship.invocable import PackageService, post


class MockDiscordApi(PackageService):
    WEBHOOK_TAG = "webhook"
    TEXT_MESSAGE_TAG = "text_message"
    CHAT_ID_KEY = "chat_id"
    PHOTO_MESSAGE_TAG = "photo_message"
    PHOTO_KEY = "photo"
    AUDIO_MESSAGE_TAG = "audio_message"
    AUDIO_KEY = "audio"
    VIDEO_MESSAGE_TAG = "video_message"
    VIDEO_KEY = "video"

    @staticmethod
    def generate_inbound_webhook_body(text: str) -> Dict:
        """Generates a Discord inbound message that conforms to a specific structure which will cause the test agent to respond with a specific media type."""
        return {
            "version": 1,
            "type": 3,
            "token": "unique_interaction_token",
            "message": {
                "type": 0,
                "tts": False,
                "timestamp": "2021-05-19T02:12:51.710000+00:00",
                "pinned": False,
                "mentions": [],
                "mention_roles": [],
                "mention_everyone": False,
                "id": "844397162624450620",
                "flags": 0,
                "embeds": [],
                "edited_timestamp": None,
                "content": "This is a message with components.",
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {"type": 2, "label": "Click me!", "style": 1, "custom_id": "click_one"}
                        ],
                    }
                ],
                "channel_id": "345626669114982402",
                "author": {
                    "username": "Mason",
                    "public_flags": 131141,
                    "id": "53908232506183680",
                    "discriminator": "1337",
                    "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
                },
                "attachments": [],
            },
            "member": {
                "user": {
                    "username": "Mason",
                    "public_flags": 131141,
                    "id": "53908232506183680",
                    "discriminator": "1337",
                    "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
                },
                "roles": ["290926798626357999"],
                "premium_since": None,
                "permissions": "17179869183",
                "pending": False,
                "nick": None,
                "mute": False,
                "joined_at": "2017-03-13T19:19:14.040000+00:00",
                "is_pending": False,
                "deaf": False,
                "avatar": None,
            },
            "id": "846462639134605312",
            "guild_id": "290926798626357999",
            "data": {"custom_id": "click_one", "component_type": 2},
            "channel_id": "345626669114982999",
            "application_id": "290926444748734465",
        }

    def send_message(self, chat_id: str, text: str):
        File.create(
            self.client,
            blocks=[],
            tags=[Tag(kind=self.TEXT_MESSAGE_TAG, name=text, value={self.CHAT_ID_KEY: chat_id})],
        )
        return "OK"

    def send_photo(
        self, chat_id: str, photo: str
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

    def send_audio(
        self, chat_id: str, audio: str
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

    def send_video(
        self, chat_id: str, video: str
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

    @post("chat.postMessage", public=True)
    def post_message(self, channel: str, text: str, blocks: List[dict]):
        """Simulate the chat.postMessage command in the Slack API."""

        for block in blocks:
            kind = block.get("type")
            if kind == "video":
                video_url = block.get("video_url")
                return self.send_video(channel, video_url)
            elif kind == "section":
                if "Audio Message" in block.get("text", {}).get("text"):
                    txt = block.get("text", {}).get("text")
                    audio_url = txt.split("<")[1].split("|")[0]
                    return self.send_audio(channel, audio_url)
                else:
                    txt = block.get("text", {}).get("text")
                    return self.send_message(channel, txt)
            elif kind == "image":
                image_url = block.get("image_url")
                return self.send_photo(channel, image_url)
        raise SteamshipError(message="Unsure how to respond")
