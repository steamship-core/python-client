from __future__ import annotations

import io
import logging
from enum import Enum
from typing import Any, List, Optional, Type, Union

from pydantic import BaseModel

from steamship.base import Client, Request, Response
from steamship.base.binary_utils import flexi_create
from steamship.base.configuration import CamelModel
from steamship.base.request import IdentifierRequest
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

    client: Client = None
    id: str = None
    handle: str = None
    mime_type: str = None
    space_id: str = None
    corpus_id: str = None
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
        corpus_id: str = None
        blocks: Optional[List[Block.CreateRequest]] = []
        tags: Optional[List[Tag.CreateRequest]] = []
        plugin_instance: str = None

        class Config:
            use_enum_values = True

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

        def to_dict(self) -> dict:
            return {"data": self.data_, "mime_type": self.mime_type}

    class ListRequest(Request):
        corpus_id: str = None

    class ListResponse(Response):
        files: List[File]

    class RawRequest(Request):
        id: str

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["file"] if "file" in obj else obj
        return super().parse_obj(obj)

    def delete(
        self, space_id: str = None, space_handle: str = None, space: Any = None
    ) -> Response[File]:
        return self.client.post(
            "file/delete",
            IdentifierRequest(id=self.id),
            expect=File,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def clear(
        self, space_id: str = None, space_handle: str = None, space: Any = None
    ) -> Response[FileClearResponse]:
        return self.client.post(
            "file/clear",
            IdentifierRequest(id=self.id),
            expect=FileClearResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    @staticmethod
    def get(
        client: Client,
        _id: str = None,
        handle: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[File]:  # TODO (Enias): Why is this a staticmethod?
        return client.post(
            "file/get",
            IdentifierRequest(id=_id, handle=handle),
            expect=File,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    @staticmethod
    def create(
        client: Client,
        filename: str = None,
        url: str = None,
        content: str = None,
        plugin_instance: str = None,
        mime_type: str = None,
        blocks: List[Block.CreateRequest] = None,
        tags: List[Tag.CreateRequest] = None,
        corpus_id: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[File]:

        if (
            filename is None
            and content is None
            and url is None
            and plugin_instance is None
            and blocks is None
        ):
            raise Exception("Either filename, content, url, or plugin Instance must be provided.")

        if blocks is not None:
            upload_type = FileUploadType.BLOCKS
        elif plugin_instance is not None:
            upload_type = FileUploadType.FILE_IMPORTER
        elif content is not None:
            # We're still going to use the file upload method for file uploads
            upload_type = FileUploadType.FILE
        elif filename is not None:
            with open(filename, "rb") as f:
                content = f.read()
            upload_type = FileUploadType.FILE
        else:
            raise Exception("Unable to determine upload type.")

        req = File.CreateRequest(
            type=upload_type,
            corpusId=corpus_id,
            url=url,
            mime_type=mime_type,
            plugin_instance=plugin_instance,
            blocks=blocks,
            tags=tags,
            filename=filename,
        )

        # Defaulting this here, as opposed to in the Engine, because it is processed by Vapor
        file_part_name = filename if filename else "unnamed"
        return client.post(
            "file/create",
            payload=req,
            file=(file_part_name, content, "multipart/form-data")
            if upload_type != FileUploadType.BLOCKS
            else None,
            expect=File,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    @staticmethod
    def list(
        client: Client,
        corpus_id: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ):
        req = File.ListRequest(corpusId=corpus_id)
        res = client.post(
            "file/list",
            payload=req,
            expect=File.ListResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )
        return res

    def refresh(self):
        return File.get(self.client, self.id)

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[FileQueryResponse]:

        req = FileQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "file/query",
            payload=req,
            expect=FileQueryResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )
        return res

    def raw(self, space_id: str = None, space_handle: str = None, space: Any = None):
        req = File.RawRequest(
            id=self.id,
        )
        # TODO (enias): Investigate why we do not need a expect here
        return self.client.post(
            "file/raw",
            payload=req,
            space_id=space_id or self.space_id,
            space_handle=space_handle,
            space=space,
            raw_response=True,
        )

    def blockify(self, plugin_instance: str = None):
        from steamship.data.operations.blockifier import BlockifyRequest
        from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput

        req = BlockifyRequest(type="file", id=self.id, plugin_instance=plugin_instance)

        return self.client.post(
            "plugin/instance/blockify",
            payload=req,
            expect=BlockAndTagPluginOutput,
            asynchronous=True,
        )

    def tag(
        self,
        plugin_instance: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[Tag]:
        # TODO (enias): Fix Circular imports
        from steamship.data.operations.tagger import TagRequest, TagResponse
        from steamship.data.plugin import PluginTargetType

        req = TagRequest(type=PluginTargetType.file, id=self.id, plugin_instance=plugin_instance)
        return self.client.post(
            "plugin/instance/tag",
            payload=req,
            expect=TagResponse,
            asynchronous=True,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def index(
        self,
        plugin_instance: str = None,
        index_id: str = None,
        e_index: EmbeddingIndex = None,
        reindex: bool = True,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
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
                space_id=space_id,
                space_handle=space_handle,
                space=space,
            ).data
        elif e_index is None:
            e_index = EmbeddingIndex(client=self.client, id=index_id)

        # We have an index available to us now. Perform the query.
        blocks = self.refresh().data.blocks

        items = []
        for block in blocks:
            item = EmbeddedItem(value=block.text, external_id=block.id, external_type="block")
            items.append(item)

        insert_task = e_index.insert_many(
            items,
            reindex=reindex,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

        insert_task.wait()
        return e_index


class FileQueryResponse(Response):
    files: List[File]


File.ListResponse.update_forward_refs()
File.CreateRequest.update_forward_refs()
