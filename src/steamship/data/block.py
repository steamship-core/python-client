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
from steamship.data.tags.tag_constants import ChatTag, DocTag, RoleTag, TagValueKey


class BlockQueryRequest(Request):
    tag_filter_query: str


class BlockUploadType(str, Enum):
    FILE = "file"  # A file uploaded as bytes or a string
    BLOCKS = "blocks"  # Blocks are sent to create a file
    URL = "url"  # content will be fetched from a URL
    NONE = "none"  # No upload; plain text only.


def get_tag_value_key(
    tags: Optional[List[Tag]], key: str, kind: Optional[str] = None, name: Optional[str] = None
) -> Optional[any]:
    """Iterates through a list of tags and returns the first that contains the provided Kind/Name/ValueKey."""
    for tag in tags or []:
        if (kind is None or tag.kind == kind) and (name is None or tag.name == name):
            return (tag.value or {}).get(key)
    return None


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
    public_data: bool = False

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
        public_data: bool = False,
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
            "publicData": public_data,
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

    def set_public_data(self, public_data: bool):
        """Set the public_data flag on this Block. If this object already exists server-side, update the flag."""
        self.public_data = public_data
        if self.client is not None and self.id is not None:
            req = {
                "id": self.id,
                "publicData": self.public_data,
            }
            return self.client.post("block/update", payload=req, expect=Block)

    def is_text(self) -> bool:
        """Return whether this is a text Block."""
        return self.mime_type == MimeTypes.TXT or (self.mime_type is None and self.text)

    def is_image(self):
        """Return whether this is an image Block."""
        return self.mime_type in [MimeTypes.PNG, MimeTypes.JPG, MimeTypes.GIF, MimeTypes.TIFF]

    def is_audio(self):
        """Return whether this is an audio Block."""
        return self.mime_type in [
            MimeTypes.MP3,
            MimeTypes.MP4_AUDIO,
            MimeTypes.WEBM_AUDIO,
            MimeTypes.WAV,
            MimeTypes.OGG_AUDIO,
        ]

    def is_video(self):
        """Return whether this is a video Block."""
        return self.mime_type in [MimeTypes.MP4_VIDEO, MimeTypes.WEBM_VIDEO, MimeTypes.OGG_VIDEO]

    @property
    def raw_data_url(self) -> Optional[str]:
        """Return a URL at which the data content of this Block can be accessed.  If public_data is True,
        this content can be accessed without an API key.
        """
        if self.client is not None:
            return f"{self.client.config.api_base}block/{self.id}/raw"
        else:
            return None

    @property
    def chat_role(self) -> Optional[RoleTag]:
        return get_tag_value_key(
            self.tags, TagValueKey.STRING_VALUE, kind=DocTag.CHAT, name=ChatTag.ROLE
        )

    def set_chat_role(self, role: RoleTag):
        return self._one_time_set_tag(
            tag_kind=DocTag.CHAT, tag_name=ChatTag.ROLE, string_value=role.value
        )

    @property
    def message_id(self) -> str:
        return get_tag_value_key(
            self.tags, TagValueKey.STRING_VALUE, kind=DocTag.CHAT, name=ChatTag.MESSAGE_ID
        )

    def set_message_id(self, message_id: str):
        return self._one_time_set_tag(
            tag_kind=DocTag.CHAT, tag_name=ChatTag.MESSAGE_ID, string_value=message_id
        )

    @property
    def chat_id(self) -> str:
        return get_tag_value_key(
            self.tags, TagValueKey.STRING_VALUE, kind=DocTag.CHAT, name=ChatTag.CHAT_ID
        )

    def set_chat_id(self, chat_id: str):
        return self._one_time_set_tag(
            tag_kind=DocTag.CHAT, tag_name=ChatTag.CHAT_ID, string_value=chat_id
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

    def as_llm_input(self, exclude_block_wrapper: Optional[bool] = False) -> str:
        if self.is_text():
            return self.text
        else:
            if exclude_block_wrapper:
                return f"{self.id}"
            return f"Block({self.id})"


class BlockQueryResponse(Response):
    blocks: List[Block]


Block.ListResponse.update_forward_refs()
Block.update_forward_refs()
