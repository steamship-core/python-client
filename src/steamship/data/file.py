from __future__ import annotations

import io
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, List, Optional, Type, Union

from pydantic import BaseModel, Field

from steamship import SteamshipError
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import GetRequest, IdentifierRequest, Request
from steamship.base.response import Response
from steamship.base.tasks import Task
from steamship.data.block import Block
from steamship.data.embeddings import EmbeddingIndex
from steamship.data.tags import Tag
from steamship.utils.binary_utils import flexi_create

if TYPE_CHECKING:
    from steamship.data.operations.tagger import TagResponse


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


class ListFileRequest(Request):
    pass


class ListFileResponse(Response):
    files: List[File]


class FileQueryRequest(Request):
    tag_filter_query: str


class File(CamelModel):
    """A file."""

    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None
    mime_type: str = None
    workspace_id: str = None
    blocks: List[Block] = []
    tags: List[Tag] = []
    filename: str = None

    class CreateRequest(Request):
        value: str = None
        data: str = None
        id: str = None
        url: str = None
        handle: str = None
        filename: str = None
        type: FileUploadType = None
        mime_type: str = None
        blocks: Optional[List[Block]] = []
        tags: Optional[List[Tag]] = []
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
        handle: str = None,
        blocks: List[Block] = None,
        tags: List[Tag] = None,
    ) -> File:

        if content is None and blocks is None:
            if tags is None:
                raise SteamshipError(message="Either filename, content, or tags must be provided.")
            else:
                content = ""
        if content is not None and blocks is not None:
            raise SteamshipError(
                message="Please provide only `blocks` or `content` to `File.create`."
            )

        if blocks is not None:
            upload_type = FileUploadType.BLOCKS
        elif content is not None:
            upload_type = FileUploadType.FILE
        else:
            raise Exception("Unable to determine upload type.")

        req = File.CreateRequest(
            handle=handle,
            type=upload_type,
            mime_type=mime_type,
            blocks=blocks,
            tags=tags,
        )

        file_data = (
            ("file-part", content, "multipart/form-data")
            if upload_type != FileUploadType.BLOCKS
            else None
        )

        # Defaulting this here, as opposed to in the Engine, because it is processed by Vapor
        return client.post(
            "file/create",
            payload=req,
            file=file_data,
            expect=File,
        )

    @staticmethod
    def create_with_plugin(
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
        refreshed = File.get(self.client, self.id)
        self.__init__(**refreshed.dict())
        self.client = refreshed.client
        return self

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

    def blockify(self, plugin_instance: str = None, wait_on_tasks: List[Task] = None) -> Task:
        from steamship.data.operations.blockifier import BlockifyRequest
        from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput

        req = BlockifyRequest(type="file", id=self.id, plugin_instance=plugin_instance)

        return self.client.post(
            "plugin/instance/blockify",
            payload=req,
            expect=BlockAndTagPluginOutput,
            wait_on_tasks=wait_on_tasks,
        )

    def tag(
        self,
        plugin_instance: str = None,
        wait_on_tasks: List[Task] = None,
    ) -> Task[TagResponse]:
        from steamship.data.operations.tagger import TagRequest, TagResponse
        from steamship.data.plugin import PluginTargetType

        req = TagRequest(type=PluginTargetType.FILE, id=self.id, plugin_instance=plugin_instance)
        return self.client.post(
            "plugin/instance/tag", payload=req, expect=TagResponse, wait_on_tasks=wait_on_tasks
        )

    def index(self, plugin_instance: Any = None) -> EmbeddingIndex:
        """Index every block in the file.

        TODO(ted): Enable indexing the results of a tag query.
        TODO(ted): It's hard to load the EmbeddingIndexPluginInstance with just a handle because of the chain
        of things that need to be created to it to function."""

        # Preserve the prior behavior of embedding the full text of each block.
        tags = [
            Tag(text=block.text, file_id=self.id, block_id=block.id, kind="block")
            for block in self.blocks or []
        ]
        return plugin_instance.insert(tags)

    @staticmethod
    def list(client: Client) -> ListFileResponse:
        return client.post(
            "file/list",
            ListFileRequest(),
            expect=ListFileResponse,
        )


class FileQueryResponse(Response):
    files: List[File]


File.CreateRequest.update_forward_refs()
ListFileResponse.update_forward_refs()
