from __future__ import annotations

import logging
from typing import Dict, List, Optional, Union

import tiktoken

from steamship import File, MimeTypes, SteamshipError
from steamship.base.client import Client
from steamship.data import TagKind
from steamship.data.block import Block
from steamship.data.tags import Tag
from steamship.data.tags.tag_constants import DocTag, RoleTag


class ChatHistory:
    class Config:
        arbitrary_types_allowed: True

    """A ChatHistory is a wrapper of a File ideal for ongoing interactions between a user and a virtual assistant."""

    file: File

    def __init__(self, file: File):
        """This init method is intended only for private use within the class. See `Chat.create()`"""
        self.file = file

    @staticmethod
    def _get_existing_file(client: Client, context_keys: Dict[str, str]) -> Optional[File]:
        """Find an existing File object whose context Tag matches the passed context keys"""
        file_query = " and ".join(
            [f'value("{key}") = {value}' for key, value in context_keys.items()]
        )
        file = File.query(client, file_query)
        if len(file.files) == 1:
            return file.files[0]
        elif len(file.files) == 0:
            return None
        else:
            raise SteamshipError(
                "Multiple ChatHistory objects have been created in this workspace with these context keys."
            )

    @staticmethod
    def get_or_create(
        client: Client,
        context_keys: Dict[str, str],
        tags: List[Tag] = None,
        initial_system_prompt: Optional[str] = None,
    ) -> ChatHistory:

        file = ChatHistory._get_existing_file(client, context_keys)

        if file is not None:
            tags = tags or []
            tags.append(Tag(kind=TagKind.DOCUMENT, name=DocTag.CHAT))

            blocks = []
            if initial_system_prompt is not None:
                blocks.append(
                    Block(
                        text=initial_system_prompt,
                        tags=[Tag(kind=TagKind.ROLE, name=RoleTag.SYSTEM)],
                    )
                )

            file = File.create(
                client=client,
                blocks=blocks,
                tags=tags,
            )
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
        tags.append(Tag(kind=TagKind.ROLE, name=RoleTag.USER))
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
        tags.append(Tag(kind=TagKind.ROLE, name=RoleTag.SYSTEM))
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
        tags.append(Tag(kind=TagKind.ROLE, name=RoleTag.ASSISTANT))
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


def token_length(block: Block, tiktoken_encoder: str = "p50k_base") -> int:
    """Calculate num tokens with tiktoken package."""
    # create a GPT-3 encoder instance
    enc = tiktoken.get_encoding(tiktoken_encoder)
    # encode the text using the GPT-3 encoder
    tokenized_text = enc.encode(block.text)
    # calculate the number of tokens in the encoded text
    return len(tokenized_text)


# TODO: abstract this into one of N possible strategies
def filter_blocks_for_prompt_length(max_tokens: int, blocks: List[Block]) -> List[int]:

    retained_blocks = []
    total_length = 0

    # Keep all system blocks
    for block in blocks:
        if block.chat_role == RoleTag.SYSTEM:
            retained_blocks.append(block)
            total_length += token_length(block)

    # If system blocks are too long, throw error
    if total_length > max_tokens:
        raise SteamshipError(
            f"Plugin attempted to filter input to fit into {max_tokens} tokens, but the total size of system blocks was {total_length}"
        )

    # Now work backwards and keep as many blocks as we can
    num_system_blocks = len(retained_blocks)
    for block in reversed(blocks):
        if block.chat_role != RoleTag.SYSTEM and total_length < max_tokens:
            block_length = token_length(block)
            if block_length + total_length < max_tokens:
                retained_blocks.append(block)
                total_length += block_length
                logging.info(f"Adding block {block.index_in_file} of token length {block_length}")

    # If we didn't add any non-system blocks, throw error
    if len(retained_blocks) == num_system_blocks:
        raise SteamshipError(
            f"Plugin attempted to filter input to fit into {max_tokens} tokens, but no non-System blocks remained."
        )

    block_indices = [block.index_in_file for block in blocks if block in retained_blocks]
    logging.info(f"Filtered input.  Total tokens {total_length} Block indices: {block_indices}")
    return block_indices
