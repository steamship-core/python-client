from __future__ import annotations

import uuid
from typing import Dict, List, Optional, Union

from steamship import File, MimeTypes, SteamshipError
from steamship.base.client import Client
from steamship.data import TagKind
from steamship.data.block import Block
from steamship.data.plugin.index_plugin_instance import EmbeddingIndexPluginInstance
from steamship.data.tags import Tag
from steamship.data.tags.tag_constants import ChatTag, DocTag, RoleTag, TagValueKey


class ChatHistory:
    """A ChatHistory is a wrapper of a File ideal for ongoing interactions between a user and a virtual assistant.
    It also includes vector-backed storage for similarity-based retrieval."""

    file: File
    embedding_index: EmbeddingIndexPluginInstance

    def __init__(self, file: File):
        """This init method is intended only for private use within the class. See `Chat.create()`"""
        self.file = file

    @staticmethod
    def _get_existing_file(client: Client, context_keys: Dict[str, str]) -> Optional[File]:
        """Find an existing File object whose memory Tag matches the passed memory keys"""
        file_query = f'kind "{TagKind.CHAT}" and name "{ChatTag.CONTEXT_KEYS}" and ' + " and ".join(
            [f'value("{key}") = "{value}"' for key, value in context_keys.items()]
        )
        file = File.query(client, file_query)
        if len(file.files) == 1:
            return file.files[0]
        elif len(file.files) == 0:
            return None
        else:
            raise SteamshipError(
                "Multiple ChatHistory objects have been created in this workspace with these memory keys."
            )

    @staticmethod
    def _get_index_handle_from_file(file: File) -> str:
        for tag in file.tags:
            if tag.kind == TagKind.CHAT and tag.name == ChatTag.INDEX_HANDLE:
                return tag.value[TagValueKey.STRING_VALUE]
        raise SteamshipError(f"Could not find index handle on file with id {file.id}")

    @staticmethod
    def get_or_create(
        client: Client,
        context_keys: Dict[str, str],
        tags: List[Tag] = None,
    ) -> ChatHistory:

        file = ChatHistory._get_existing_file(client, context_keys)

        if file is None:
            tags = tags or []
            index_handle = str(uuid.uuid4())
            tags.append(Tag(kind=TagKind.DOCUMENT, name=DocTag.CHAT))
            tags.append(Tag(kind=TagKind.CHAT, name=ChatTag.CONTEXT_KEYS, value=context_keys))
            tags.append(
                Tag(
                    kind=TagKind.CHAT,
                    name=ChatTag.INDEX_HANDLE,
                    value={TagValueKey.STRING_VALUE: index_handle},
                )
            )

            blocks = []
            file = File.create(
                client=client,
                blocks=blocks,
                tags=tags,
            )
            embedding_index = EmbeddingIndexPluginInstance.create(handle=index_handle)
        else:
            index_handle = ChatHistory._get_index_handle_from_file(file)
            embedding_index = EmbeddingIndexPluginInstance.get(client, index_handle)

        print(embedding_index)
        return ChatHistory(file)

    def append_user_message(
        self,
        text: str = None,
        tags: List[Tag] = None,
        content: Union[str, bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[MimeTypes] = None,
    ) -> Block:
        """Append a new block to this with content provided by the end-user."""
        tags = tags or []
        tags.append(
            Tag(
                kind=TagKind.CHAT, name=ChatTag.ROLE, value={TagValueKey.STRING_VALUE: RoleTag.USER}
            )
        )
        return self.file.append_block(
            text=text, tags=tags, content=content, url=url, mime_type=mime_type
        )

    def append_system_message(
        self,
        text: str = None,
        tags: List[Tag] = None,
        content: Union[str, bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[MimeTypes] = None,
    ) -> Block:
        """Append a new block to this with content provided by the system, i.e., instructions to the assistant."""
        tags = tags or []
        tags.append(
            Tag(
                kind=TagKind.CHAT,
                name=ChatTag.ROLE,
                value={TagValueKey.STRING_VALUE: RoleTag.SYSTEM},
            )
        )
        return self.file.append_block(
            text=text, tags=tags, content=content, url=url, mime_type=mime_type
        )

    def append_agent_message(
        self,
        text: str = None,
        tags: List[Tag] = None,
        content: Union[str, bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[MimeTypes] = None,
    ) -> Block:
        """Append a new block to this with content provided by the agent, i.e., results from the assistant."""
        tags = tags or []
        tags.append(
            Tag(
                kind=TagKind.CHAT,
                name=ChatTag.ROLE,
                value={TagValueKey.STRING_VALUE: RoleTag.ASSISTANT},
            )
        )
        return self.file.append_block(
            text=text, tags=tags, content=content, url=url, mime_type=mime_type
        )

    @property
    def last_user_message(self) -> Optional[Block]:
        for block in self.file.blocks[::-1]:
            if block.chat_role == RoleTag.USER:
                return block
        return None

    @property
    def last_system_message(self) -> Optional[Block]:
        for block in self.file.blocks[::-1]:
            if block.chat_role == RoleTag.SYSTEM:
                return block
        return None

    @property
    def last_agent_message(self) -> Optional[Block]:
        for block in self.file.blocks[::-1]:
            if block.chat_role == RoleTag.ASSISTANT:
                return block
        return None

    @property
    def initial_system_prompt(self) -> Optional[Block]:
        if len(self.file.blocks) > 0 and self.file.blocks[0].chat_role == RoleTag.SYSTEM:
            return self.file.blocks[0]
        else:
            return None

    def refresh(self):
        self.file.refresh()

    @property
    def tags(self) -> List[Tag]:
        return self.file.tags

    @property
    def messages(self) -> List[Block]:
        return self.file.blocks

    @property
    def client(self) -> Client:
        return self.file.client
