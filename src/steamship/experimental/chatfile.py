from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Union

import tiktoken

from steamship import File, MimeTypes, SteamshipError
from steamship.base.client import Client
from steamship.base.request import IdentifierRequest
from steamship.base.tasks import Task
from steamship.data import TagKind
from steamship.data.block import Block
from steamship.data.file import ListFileRequest, ListFileResponse
from steamship.data.tags import Tag
from steamship.data.tags.tag_constants import DocTag, RoleTag

if TYPE_CHECKING:
    from steamship.data.operations.generator import GenerateResponse


class ListChatResponse:  # not a pydantic model
    chats: List[ChatFile]

    @staticmethod
    def from_list_file_response(list_file_response: ListFileResponse) -> ListChatResponse:
        result = ListChatResponse()
        result.chats = [ChatFile(file) for file in list_file_response.files]
        return result


# Local tag kinds
CHAT_GENERATOR_INSTANCE_HANDLE = "chat-generator-instance-handle"
MAX_GENERATION_TOKENS = "max-generation-tokens"


class ChatFile:
    """A Chat is a wrapper of a File ideal for ongoing interactions between a user and a virtual assistant."""

    generator_instance_handle: str
    file: File
    max_generation_tokens: Optional[int]

    def __init__(self, file: File):
        """This init method is intended only for private use within the class. See `Chat.create()`"""
        self.file = file
        self._get_plugin_instance_from_tag()
        self._get_max_generation_tokens_from_tag()

    def _get_plugin_instance_from_tag(self):
        for tag in self.file.tags:
            if tag.kind == CHAT_GENERATOR_INSTANCE_HANDLE:
                self.generator_instance_handle = tag.name
        if self.generator_instance_handle is None:
            raise SteamshipError(
                f"Attempted to load file with handle {self.file.handle} as a Chat, but it had no generator instance handle"
            )

    def _get_max_generation_tokens_from_tag(self):
        for tag in self.file.tags:
            if tag.kind == MAX_GENERATION_TOKENS:
                self.max_generation_tokens = int(tag.name)
        self.max_generation_tokens = None

    @staticmethod
    def get(
        client: Client,
        _id: str = None,
        handle: str = None,
    ) -> ChatFile:
        file = client.post(
            "file/get",
            IdentifierRequest(id=_id, handle=handle),
            expect=ChatFile,
        )
        return ChatFile(file)

    @staticmethod
    def create(
        client: Client,
        generator_instance_handle: str,
        content: Union[str, bytes] = None,
        max_generation_tokens: Optional[int] = None,
        mime_type: MimeTypes = None,
        handle: str = None,
        blocks: List[Block] = None,
        tags: List[Tag] = None,
        initial_system_prompt: Optional[str] = None,
    ) -> ChatFile:

        tags = tags or []
        tags.append(Tag(kind=TagKind.DOCUMENT, name=DocTag.CHAT))
        tags.append(Tag(kind=CHAT_GENERATOR_INSTANCE_HANDLE, name=generator_instance_handle))
        if max_generation_tokens is not None:
            tags.append(Tag(kind=MAX_GENERATION_TOKENS, name=str(max_generation_tokens)))

        if initial_system_prompt is not None:
            blocks = blocks or []
            blocks.append(
                Block(
                    text=initial_system_prompt, tags=[Tag(kind=TagKind.ROLE, name=RoleTag.SYSTEM)]
                )
            )

        file = File.create(
            client=client,
            content=content,
            mime_type=mime_type,
            handle=handle,
            blocks=blocks,
            tags=tags,
        )
        return ChatFile(file)

    @staticmethod
    def list(client: Client) -> ListChatResponse:
        files: ListFileResponse = client.post(
            "file/list",
            ListFileRequest(),
            expect=ListFileResponse,
        )
        return ListChatResponse.from_list_file_response(files)

    def append_user_block(
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

    def append_system_block(
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

    def generate_next_response(
        self,
        start_block_index: int = None,
        end_block_index: Optional[int] = None,
        append_output_to_file: bool = True,
        options: Optional[dict] = None,
    ) -> Task[GenerateResponse]:
        """Append a new block to this with content provided by the generation plugin (assistant).
        Assumes output will be appended to this chat, or not stored at all.
        """
        if self.max_generation_tokens is None:
            return self.file.generate(
                plugin_instance_handle=self.generator_instance_handle,
                start_block_index=start_block_index,
                end_block_index=end_block_index,
                append_output_to_file=append_output_to_file,
                options=options,
            )
        else:
            block_indices = filter_blocks_for_prompt_length(
                self.max_generation_tokens, self.file.blocks[start_block_index:end_block_index]
            )
            if start_block_index is not None:
                block_indices = [index + start_block_index for index in block_indices]
            return self.file.generate(
                plugin_instance_handle=self.generator_instance_handle,
                block_index_list=block_indices,
                append_output_to_file=append_output_to_file,
                options=options,
            )

    def refresh(self):
        self.file.refresh()

    @property
    def tags(self) -> List[Tag]:
        return self.file.tags

    @property
    def blocks(self) -> List[Block]:
        return self.file.blocks

    @property
    def client(self) -> Client:
        return self.file.client


class ChatQueryResponse:  # Not a pydantic type
    chats: List[ChatFile]


def block_role(block: Block) -> RoleTag:
    for tag in block.tags:
        if tag.kind == TagKind.ROLE:
            return RoleTag(tag.name)


def token_length(block: Block, tiktoken_encoder: str = "p50k_base") -> int:
    """Calculate num tokens with tiktoken package."""
    # create a GPT-3 encoder instance
    enc = tiktoken.get_encoding(tiktoken_encoder)
    # encode the text using the GPT-3 encoder
    tokenized_text = enc.encode(block.text)
    # calculate the number of tokens in the encoded text
    return len(tokenized_text)


def filter_blocks_for_prompt_length(max_tokens: int, blocks: List[Block]) -> List[int]:

    retained_blocks = []
    total_length = 0

    # Keep all system blocks
    for block in blocks:
        if block_role(block) == RoleTag.SYSTEM:
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
        if block_role(block) != RoleTag.SYSTEM and total_length < max_tokens:
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


# ChatQueryResponse.update_forward_refs()
