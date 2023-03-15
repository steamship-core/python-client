from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

from steamship import File, MimeTypes
from steamship.base.client import Client
from steamship.base.request import IdentifierRequest
from steamship.base.response import Response
from steamship.base.tasks import Task
from steamship.data import TagKind
from steamship.data.block import Block
from steamship.data.file import FileQueryRequest, ListFileRequest
from steamship.data.tags import Tag
from steamship.data.tags.tag_constants import DocTag, RoleTag

if TYPE_CHECKING:
    from steamship.data.operations.generator import GenerateResponse


class ListChatResponse(Response):
    files: List[Chat]


class Chat(File):
    """A Chat is a subclass of a File ideal for ongoing interactions between a user and a virtual assistant."""

    @staticmethod
    def get(
        client: Client,
        _id: str = None,
        handle: str = None,
    ) -> File:
        return client.post(
            "file/get",
            IdentifierRequest(id=_id, handle=handle),
            expect=Chat,
        )

    @staticmethod
    def create(
        client: Client,
        content: Union[str, bytes] = None,
        mime_type: MimeTypes = None,
        handle: str = None,
        blocks: List[Block] = None,
        tags: List[Tag] = None,
    ) -> Chat:

        tags = tags or []
        tags.append(Tag(kind=TagKind.DOCUMENT, name=DocTag.CHAT))
        return File._create(
            client=client,
            expect=Chat,
            content=content,
            mime_type=mime_type,
            handle=handle,
            blocks=blocks,
            tags=tags,
        )

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
    ) -> ChatQueryResponse:

        req = FileQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "file/query",
            payload=req,
            expect=ChatQueryResponse,
        )
        return res

    @staticmethod
    def list(client: Client) -> ListChatResponse:
        return client.post(
            "file/list",
            ListFileRequest(),
            expect=ListChatResponse,
        )

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
        return self.append_block(
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
        return self.append_block(
            text=text, tags=tags, content=content, url=url, mime_type=mime_type
        )

    def generate_next_response(
        self,
        plugin_instance_handle: str,
        start_block_index: int = None,
        end_block_index: Optional[int] = None,
        append_output_to_file: bool = True,
        options: Optional[dict] = None,
    ) -> Task[GenerateResponse]:
        """Append a new block to this with content provided by the generation plugin (assistant).
        Assumes output will be appended to this chat, or not stored at all.
        """
        return self.generate(
            plugin_instance_handle=plugin_instance_handle,
            start_block_index=start_block_index,
            end_block_index=end_block_index,
            append_output_to_file=append_output_to_file,
            options=options,
        )


class ChatQueryResponse(Response):
    files: List[Chat]


ChatQueryResponse.update_forward_refs()
