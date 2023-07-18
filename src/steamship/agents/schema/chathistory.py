from __future__ import annotations

import uuid
from typing import Dict, List, Optional, Union, cast

from steamship import File, MimeTypes, Steamship, SteamshipError, Task
from steamship.agents.schema.message_selectors import MessageSelector
from steamship.agents.schema.text_splitters import FixedSizeTextSplitter, TextSplitter
from steamship.base.client import Client
from steamship.data import TagKind
from steamship.data.block import Block
from steamship.data.plugin.index_plugin_instance import EmbeddingIndexPluginInstance, SearchResults
from steamship.data.tags import Tag
from steamship.data.tags.tag_constants import ChatTag, DocTag, RoleTag, TagValueKey


class ChatHistory:
    """A ChatHistory is a wrapper of a File ideal for ongoing interactions between a user and a virtual assistant.
    It also includes vector-backed storage for similarity-based retrieval."""

    file: File
    embedding_index: EmbeddingIndexPluginInstance
    text_splitter: TextSplitter

    def __init__(
        self,
        file: File,
        embedding_index: Optional[EmbeddingIndexPluginInstance],
        text_splitter: TextSplitter = None,
    ):
        """This init method is intended only for private use within the class. See `Chat.create()`"""
        self.file = file
        self.embedding_index = embedding_index
        if text_splitter is not None:
            self.text_splitter = text_splitter
        else:
            self.text_splitter = FixedSizeTextSplitter(chunk_size=300)

    @staticmethod
    def _get_existing_file(client: Client, context_keys: Dict[str, str]) -> Optional[File]:
        """Find an existing File object whose memory Tag matches the passed memory keys"""
        file_query = (
            f'kind "{TagKind.CHAT}" and name "{ChatTag.CONTEXT_KEYS}"'
            + (" and " if len(context_keys) > 0 else "")
            + " and ".join([f'value("{key}") = "{value}"' for key, value in context_keys.items()])
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
    def _get_embedding_index(client: Steamship, index_handle: str) -> EmbeddingIndexPluginInstance:
        return cast(
            EmbeddingIndexPluginInstance,
            client.use_plugin(
                plugin_handle="embedding-index",
                instance_handle=index_handle,
                config={
                    "embedder": {
                        "plugin_handle": "openai-embedder",
                        "plugin_instance-handle": "text-embedding-ada-002",
                        "fetch_if_exists": True,
                        "config": {"model": "text-embedding-ada-002", "dimensionality": 1536},
                    }
                },
                fetch_if_exists=True,
            ),
        )

    @staticmethod
    def get_or_create(
        client: Steamship,
        context_keys: Dict[str, str],
        tags: List[Tag] = None,
        searchable: bool = True,
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
        else:
            index_handle = ChatHistory._get_index_handle_from_file(file)

        if searchable:
            embedding_index = ChatHistory._get_embedding_index(client, index_handle)
        else:
            embedding_index = None

        return ChatHistory(file, embedding_index)

    def append_message_with_role(
        self,
        text: str = None,
        role: RoleTag = RoleTag.USER,
        tags: List[Tag] = None,
        content: Union[str, bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[MimeTypes] = None,
    ) -> Block:
        """Append a new block to this with content provided by the end-user."""
        tags = tags or []
        tags.append(
            Tag(kind=TagKind.CHAT, name=ChatTag.ROLE, value={TagValueKey.STRING_VALUE: role})
        )
        block = self.file.append_block(
            text=text, tags=tags, content=content, url=url, mime_type=mime_type
        )
        if self.embedding_index is not None:
            chunk_tags = self.text_splitter.chunk_text_to_tags(
                block, kind=TagKind.CHAT, name=ChatTag.CHUNK
            )
            block.tags.extend(chunk_tags)
            self.embedding_index.insert(chunk_tags)
        return block

    def append_user_message(
        self,
        text: str = None,
        tags: List[Tag] = None,
        content: Union[str, bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[MimeTypes] = None,
    ) -> Block:
        """Append a new block to this with content provided by the end-user."""
        return self.append_message_with_role(text, RoleTag.USER, tags, content, url, mime_type)

    def append_system_message(
        self,
        text: str = None,
        tags: List[Tag] = None,
        content: Union[str, bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[MimeTypes] = None,
    ) -> Block:
        """Append a new block to this with content provided by the system, i.e., instructions to the assistant."""
        return self.append_message_with_role(text, RoleTag.SYSTEM, tags, content, url, mime_type)

    def append_assistant_message(
        self,
        text: str = None,
        tags: List[Tag] = None,
        content: Union[str, bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[MimeTypes] = None,
    ) -> Block:
        """Append a new block to this with content provided by the agent, i.e., results from the assistant."""
        return self.append_message_with_role(text, RoleTag.ASSISTANT, tags, content, url, mime_type)

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

    def select_messages(self, selector: MessageSelector) -> List[Block]:
        return selector.get_messages(self.messages)

    def search(self, text: str, k=None) -> Task[SearchResults]:
        if self.embedding_index is None:
            raise SteamshipError("This ChatHistory has no embedding index and is not searchable.")
        return self.embedding_index.search(text, k)

    def is_searchable(self) -> bool:
        return self.embedding_index is not None

    def delete_messages(self, selector: MessageSelector):
        """Delete a set of selected messages from the ChatHistory.

        If `selector == None`, no messages will be deleted.

        NOTES:
        - upon deletion, refresh() is called to ensure up-to-date history refs.
        - causes a full re-index of chat history if the history is searchable.
        """
        if selector:
            selected_messages = selector.get_messages(self.messages)
            for msg in selected_messages:
                msg.delete()

            self.refresh()
            if self.is_searchable():
                self.embedding_index.reset()
                for msg in self.messages:
                    for tag in msg.tags:
                        if tag.kind == TagKind.CHAT and tag.name == ChatTag.CHUNK:
                            # TODO(dougreid): figure out why tag.text gets lost.
                            if not tag.text:
                                tag.text = msg.text[tag.start_idx : tag.end_idx]
                            self.embedding_index.insert(tag)

        self.refresh()

    def clear(self):
        """Deletes ALL messages from the ChatHistory (including system).

        NOTE: upon deletion, refresh() is called to ensure up-to-date history refs.
        """
        for block in self.file.blocks:
            block.delete()

        if self.is_searchable():
            self.embedding_index.reset()

        self.refresh()
