from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional, Type, Union

import requests
from pydantic import BaseModel, Field

from steamship import MimeTypes, SteamshipError
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import DeleteRequest, IdentifierRequest, Request
from steamship.base.response import Response
from steamship.data.tags.tag import Tag


class BlockQueryRequest(Request):
    tag_filter_query: str


class BlockUploadType(str, Enum):
    FILE = "file"  # A file uploaded as bytes or a string
    BLOCKS = "blocks"  # Blocks are sent to create a file
    URL = "url"  # content will be fetched from a URL
    NONE = "none"  # No upload; plain text only


class Block(CamelModel):
    """A Block is a chunk of content within a File. It can be plain text content, image content,
    video content, etc. If the content is not text, the text value may be the empty string
    for backwards compatibility.
    """

    client: Client = Field(None, exclude=True)
    id: str = None
    file_id: str = None
    text: str = None
    tags: Optional[List[Tag]] = []
    index_in_file: Optional[int] = Field(alias="index")
    mime_type: Optional[MimeTypes]
    url: Optional[
        str
    ] = None  # Only for creation of blocks; used to fetch content from a public URL.
    content_url: Optional[
        str
    ] = None  # For overriding the URL of the raw data for ephemeral blocks. Setting this will have no effect
    upload_type: Optional[
        BlockUploadType
    ] = None  # for returning Blocks as the result of a generate request
    upload_bytes: Optional[
        bytes
    ] = None  # ONLY for returning Blocks as the result of a generate request. Will not be set when receiving blocks from the server. See raw()

    class ListRequest(Request):
        file_id: str = None

    class ListResponse(Response):
        blocks: List[Block] = []

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["block"] if "block" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def get(
        client: Client,
        _id: str = None,
    ) -> Block:
        return client.post(
            "block/get",
            IdentifierRequest(id=_id),
            expect=Block,
        )

    @staticmethod
    def create(
        client: Client,
        file_id: str,
        text: str = None,
        tags: List[Tag] = None,
        content: Union[str, bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[MimeTypes] = None,
    ) -> Block:
        """
        Create a new Block within a File specified by file_id.

        You can create a Block in several ways:
        - Providing raw text as the text parameter;
        - Providing the content of the block as string or bytes;
        - Providing a publicly accessible URL where the content is stored.

        """

        if content is not None and url is not None:
            raise SteamshipError("May provide content or URL, but not both when creating a Block")

        if content is not None:
            upload_type = BlockUploadType.FILE
        elif url is not None:
            upload_type = BlockUploadType.URL
        else:
            upload_type = BlockUploadType.NONE

        req = {
            "fileId": file_id,
            "text": text,
            "tags": [t.dict(by_alias=True) for t in tags] if tags else [],
            "url": url,
            "mimeType": mime_type,
            "uploadType": upload_type,
        }

        file_data = (
            ("file-part", content, "multipart/form-data")
            if upload_type == BlockUploadType.FILE
            else None
        )

        return client.post(
            "block/create",
            req,
            expect=Block,
            file=file_data,
        )

    def delete(self) -> Block:
        return self.client.post(
            "block/delete",
            DeleteRequest(id=self.id),
            expect=Tag,
        )

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
    ) -> BlockQueryResponse:
        req = BlockQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "block/query",
            payload=req,
            expect=BlockQueryResponse,
        )
        return res

    def index(self, embedding_plugin_instance: Any = None):
        """Index this block."""
        tags = [
            Tag(
                text=self.text,
                file_id=self.file_id,
                block_id=self.id,
                kind="block",
                start_idx=0,
                end_idx=len(self.text),
            )
        ]
        return embedding_plugin_instance.insert(tags)

    def raw(self):
        if self.content_url is not None:
            return requests.get(self.content_url).content
        else:
            return self.client.post(
                "block/raw",
                payload={
                    "id": self.id,
                },
                raw_response=True,
            )

    def is_text(self) -> bool:
        """Return whether this is a text Block."""
        return self.mime_type == MimeTypes.TXT

    def is_image(self):
        """Return whether this is an image Block."""
        return self.mime_type in [MimeTypes.PNG, MimeTypes.JPG, MimeTypes.GIF, MimeTypes.TIFF]

    def is_audio(self):
        """Return whether this is an audio Block."""
        return self.mime_type in [MimeTypes.MP3, MimeTypes.MP4_AUDIO, MimeTypes.WEBM_AUDIO]

    def is_video(self):
        """Return whether this is a video Block."""
        return self.mime_type in [MimeTypes.MP4_VIDEO, MimeTypes.WEBM_VIDEO]


class BlockQueryResponse(Response):
    blocks: List[Block]


Block.ListResponse.update_forward_refs()
Block.update_forward_refs()
