from typing import Optional

from steamship import Block, SteamshipError, Tag
from steamship.data.tags.tag_constants import ChatTag, DocTag, TagValueKey
from steamship.experimental.easy.tags import get_tag_value_key


class ChatMessage(Block):
    """A Block with helper functions specific to being a message in a chat."""

    def __init__(self, chat_id: Optional[str] = None, message_id: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)

        # These methods will result in back-end persistence in addition to local object modification.
        if chat_id:
            self.set_chat_id(chat_id)

        if message_id:
            self.set_message_id(message_id)

    @staticmethod
    def from_block(block: Block, chat_id: Optional[str] = None, message_id: Optional[str] = None):
        return ChatMessage(
            chat_id=chat_id,
            message_id=message_id,
            client=block.client,
            id=block.id,
            file_id=block.file_id,
            text=block.text,
            tags=block.tags,
            index_in_file=block.index_in_file,
            mime_type=block.mime_type,
            url=block.url,
            content_url=block.content_url,
            upload_type=block.upload_type,
            upload_bytes=block.upload_bytes,
        )

    def set_chat_id(self, chat_id: str):
        """Set the Chat ID that this ChatMessage belongs to, updating the local tagset as well."""
        # NB: The str() wrapper below is important: sends int values for these fields but we need a standard.
        #     representation internally. String is more extensible than int, so it will be up to any Telegram
        #     handler to re-interpret these values back as strings.
        chat_id = str(chat_id)
        return self._one_time_set_tag(
            tag_kind=DocTag.CHAT, tag_name=ChatTag.CHAT_ID, string_value=chat_id
        )

    def set_message_id(self, message_id: str):
        """Set the Message ID that this ChatMessage belongs to, updating the local tagset as well."""
        # NB: The str() wrapper below is important: sends int values for these fields but we need a standard.
        #     representation internally. String is more extensible than int, so it will be up to any Telegram
        #     handler to re-interpret these values back as strings.
        message_id = str(message_id)
        return self._one_time_set_tag(
            tag_kind=DocTag.CHAT, tag_name=ChatTag.MESSAGE_ID, string_value=message_id
        )

    def get_chat_id(self) -> str:
        """Return the Chat ID that this ChatMessage belongs to."""
        return get_tag_value_key(
            self.tags, TagValueKey.STRING_VALUE, kind=DocTag.CHAT, name=ChatTag.CHAT_ID
        )

    def get_message_id(self) -> str:
        """Return the Message ID that this ChatMessage belongs to."""
        return get_tag_value_key(
            self.tags, TagValueKey.STRING_VALUE, kind=DocTag.CHAT, name=ChatTag.MESSAGE_ID
        )

    def _one_time_set_tag(self, tag_kind: str, tag_name: str, string_value: str):
        existing = get_tag_value_key(
            self.tags, TagValueKey.STRING_VALUE, kind=tag_kind, name=tag_name
        )

        if existing is not None:
            if existing == string_value:
                return  # No action necessary
            else:
                raise SteamshipError(
                    message=f"Block {self.id} already has an existing {tag_kind}/{tag_name} with value {existing}. Unable to set to {string_value}"
                )

        if self.client and self.id:
            tag = Tag.create(
                self.client,
                file_id=self.file_id,
                block_id=self.id,
                kind=tag_kind,
                name=tag_name,
                value={TagValueKey.STRING_VALUE: string_value},
            )
        else:
            tag = Tag(
                kind=tag_kind,
                name=tag_name,
                value={TagValueKey.STRING_VALUE: string_value},
            )

        self.tags.append(tag)
