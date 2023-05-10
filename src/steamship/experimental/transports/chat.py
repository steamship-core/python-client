from typing import Optional

from steamship import Block, SteamshipError, Tag
from steamship.data.tags.tag_constants import ChatTag, DocTag, TagValueKey
from steamship.experimental.easy.tags import get_tag_value_key


class ChatMessage(Block):
    def __init__(self, chat_id: Optional[str] = None, message_id: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)

        # Note: Keep the str() wrappings below since Telegram sends int values.
        # The TelegramTransport will take care of re-int-ifying them.

        if chat_id:
            self.set_chat_id(chat_id)

        if message_id:
            self.set_message_id(message_id)

    def set_chat_id(self, chat_id: str):
        existing = self.get_chat_id()
        if existing is not None:
            if existing == chat_id:
                return  # No action necessary
            else:
                raise SteamshipError(
                    message=f"Block {self.id} already has an existing chat id {existing}. Unable to set to {chat_id}"
                )

        if self.client and self.id:
            tag = Tag.create(
                self.client,
                file_id=self.file_id,
                block_id=self.id,
                kind=DocTag.CHAT,
                name=ChatTag.CHAT_ID,
                value={TagValueKey.STRING_VALUE: str(chat_id)},
            )
        else:
            tag = Tag(
                kind=DocTag.CHAT,
                name=ChatTag.CHAT_ID,
                value={TagValueKey.STRING_VALUE: str(chat_id)},
            )

        self.tags.append(tag)

    def set_message_id(self, message_id: str):
        existing = self.get_message_id()
        if existing is not None:
            if existing == message_id:
                return  # No action necessary
            else:
                raise SteamshipError(
                    message=f"Block {self.id} already has an existing message_id {existing}. Unable to set to {message_id}"
                )

        if self.client and self.id:
            tag = Tag.create(
                self.client,
                file_id=self.file_id,
                block_id=self.id,
                kind=DocTag.CHAT,
                name=ChatTag.MESSAGE_ID,
                value={TagValueKey.STRING_VALUE: str(message_id)},
            )
        else:
            tag = Tag(
                kind=DocTag.CHAT,
                name=ChatTag.MESSAGE_ID,
                value={TagValueKey.STRING_VALUE: str(message_id)},
            )

        self.tags.append(tag)

    def get_chat_id(self) -> str:
        return get_tag_value_key(
            self.tags, TagValueKey.STRING_VALUE, kind=DocTag.CHAT, name=ChatTag.CHAT_ID
        )

    def get_message_id(self) -> str:
        return get_tag_value_key(
            self.tags, TagValueKey.STRING_VALUE, kind=DocTag.CHAT, name=ChatTag.MESSAGE_ID
        )
