from __future__ import annotations

import io
import logging
from enum import Enum
from typing import Any, List, Optional, Type, Union

from pydantic import BaseModel, Field

from steamship.base import Client, Request, Response, Task
from steamship.base.binary_utils import flexi_create
from steamship.base.configuration import CamelModel
from steamship.base.request import GetRequest, IdentifierRequest
from steamship.data.block import Block
from steamship.data.embeddings import EmbeddingIndex
from steamship.data.tags import Tag


class FileUploadType(str, Enum):
    FILE = "file"  # The CreateRequest contains a file upload that should be used
    VALUE = "value"  # The Create Request contains a `text` field that should be used
    FILE_IMPORTER = (
        "fileImporter"  # The CreateRequest contains a fileImporter handle that should be used
    )
    BLOCKS = "blocks"  # The CreateRequest contains blocks and tags that should be read in directly


_logger = logging.getLogger(__name__)


class FileClearResponse(Response):
    id: str


class FileQueryRequest(Request):
    tag_filter_query: str


class File(CamelModel):
    """A file."""

    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None
    mime_type: str = None
    space_id: str = None
    blocks: List[Block] = []
    tags: List[Tag] = []
    filename: str = None

    class CreateRequest(Request):
        value: str = None
        data: str = None
        id: str = None
        url: str = None
        filename: str = None
        type: FileUploadType = None
        mime_type: str = None
        blocks: Optional[List[Block.CreateRequest]] = []
        tags: Optional[List[Tag.CreateRequest]] = []
        plugin_instance: str = None

    class CreateResponse(Response):
        data_: Any = None
        mime_type: str = None

        def __init__(
            self,
            data: Any = None,
            string: str = None,
            _bytes: Union[bytes, io.BytesIO] = None,
            json: io.BytesIO = None,
            mime_type: str = None,
        ):
            super().__init__()
            data, mime_type, encoding = flexi_create(
                data=data, string=string, json=json, _bytes=_bytes, mime_type=mime_type
            )
            self.data_ = data
            self.mime_type = mime_type

        @classmethod
        def parse_obj(cls: Type[BaseModel], obj: Any) -> Response:
            obj["data"] = obj.get("data") or obj.get("data_")
            if "data_" in obj:
                del obj["data_"]
            return super().parse_obj(obj)

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["file"] if "file" in obj else obj
        return super().parse_obj(obj)

    def delete(self) -> File:
        return self.client.post(
            "file/delete",
            IdentifierRequest(id=self.id),
            expect=File,
        )

    @staticmethod
    def get(
        client: Client,
        _id: str = None,
        handle: str = None,
    ) -> File:
        return client.post(
            "file/get",
            IdentifierRequest(id=_id, handle=handle),
            expect=File,
        )

    @staticmethod
    def create(
        client: Client,
        content: Union[str, bytes] = None,
        mime_type: str = None,
        blocks: List[Block.CreateRequest] = None,
        tags: List[Tag.CreateRequest] = None,
    ) -> File:

        if content is None and blocks is None and tags is None:
            raise Exception("Either filename, content, url, or plugin Instance must be provided.")

        if blocks is not None or tags is not None:
            upload_type = FileUploadType.BLOCKS
        elif content is not None:
            upload_type = FileUploadType.FILE
        else:
            raise Exception("Unable to determine upload type.")

        req = File.CreateRequest(
            type=upload_type,
            mime_type=mime_type,
            blocks=blocks,
            tags=tags,
        )

        # Defaulting this here, as opposed to in the Engine, because it is processed by Vapor
        return client.post(
            "file/create",
            payload=req,
            file=("file-part", content, "multipart/form-data")
            if upload_type != FileUploadType.BLOCKS
            else None,
            expect=File,
        )

    @staticmethod
    def create_plugin(
        client: Client,
        plugin_instance: str,
        url: str = None,
        mime_type: str = None,
    ) -> Task[File]:

        req = File.CreateRequest(
            type=FileUploadType.FILE_IMPORTER,
            url=url,
            mime_type=mime_type,
            plugin_instance=plugin_instance,
        )

        return client.post("file/create", payload=req, expect=File, as_background_task=True)

    def refresh(self) -> File:
        return File.get(self.client, self.id)

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
    ) -> FileQueryResponse:

        req = FileQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "file/query",
            payload=req,
            expect=FileQueryResponse,
        )
        return res

    def raw(self):
        return self.client.post(
            "file/raw",
            payload=GetRequest(
                id=self.id,
            ),
            raw_response=True,
        )

    def blockify(self, plugin_instance: str = None) -> Task:
        from steamship.data.operations.blockifier import BlockifyRequest
        from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput

        req = BlockifyRequest(type="file", id=self.id, plugin_instance=plugin_instance)

        return self.client.post(
            "plugin/instance/blockify",
            payload=req,
            expect=BlockAndTagPluginOutput,
        )

    def tag(
        self,
        plugin_instance: str = None,
    ) -> Task[Tag]:
        # TODO (enias): Fix Circular imports
        from steamship.data.operations.tagger import TagRequest, TagResponse
        from steamship.data.plugin import PluginTargetType

        req = TagRequest(type=PluginTargetType.file, id=self.id, plugin_instance=plugin_instance)
        return self.client.post(
            "plugin/instance/tag",
            payload=req,
            expect=TagResponse,
        )

    def index(
        self,
        plugin_instance: str = None,
        index_id: str = None,
        e_index: EmbeddingIndex = None,
        reindex: bool = True,
    ) -> EmbeddingIndex:
        # TODO: This should really be done all on the app, but for now we'll do it in the client
        # to facilitate demos.
        from steamship import EmbeddingIndex
        from steamship.data.embeddings import EmbeddedItem

        if index_id is None and e_index is not None:
            index_id = e_index.id

        if index_id is None and e_index is None:
            e_index = EmbeddingIndex.create(
                client=self.client,
                plugin_instance=plugin_instance,
                upsert=True,
            )
        elif e_index is None:
            e_index = EmbeddingIndex(client=self.client, id=index_id)

        # We have an index available to us now. Perform the query.
        blocks = self.refresh().blocks

        items = []
        for block in blocks:
            item = EmbeddedItem(value=block.text, external_id=block.id, external_type="block")
            items.append(item)

        _ = e_index.insert_many(
            items,
            reindex=reindex,
        )

        return e_index


class FileQueryResponse(Response):
    files: List[File]


File.CreateRequest.update_forward_refs()
