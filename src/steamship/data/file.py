from __future__ import annotations

import io
import mimetypes
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Type, Union

from pydantic import BaseModel, Field

from steamship import MimeTypes, SteamshipError
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import GetRequest, IdentifierRequest, ListRequest, Request, SortOrder
from steamship.base.response import ListResponse, Response
from steamship.base.tasks import Task
from steamship.data.block import Block
from steamship.data.embeddings import EmbeddingIndex
from steamship.data.tags import Tag, TagKind
from steamship.data.tags.tag_constants import ProvenanceTag
from steamship.utils.binary_utils import flexi_create

if TYPE_CHECKING:
    from steamship.data.operations.generator import GenerateResponse
    from steamship.data.operations.tagger import TagResponse


class FileUploadType(str, Enum):
    FILE = "file"  # A file uploaded as bytes or a string
    FILE_IMPORTER = "fileImporter"  # A fileImporter will be used to create the file
    BLOCKS = "blocks"  # Blocks are sent to create a file
    NONE = "none"  # Create an empty file


class FileClearResponse(Response):
    id: str


class ListFileRequest(ListRequest):
    pass


class ListFileResponse(ListResponse):
    files: List[File]


class FileQueryRequest(Request):
    tag_filter_query: str


class File(CamelModel):
    """A file."""

    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None
    mime_type: MimeTypes = None
    workspace_id: str = None
    blocks: List[Block] = []
    tags: List[Tag] = []
    filename: str = None
    public_data: bool = False

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
        mime_type: MimeTypes = None,
        handle: str = None,
        blocks: List[Block] = None,
        tags: List[Tag] = None,
        public_data: bool = False,
    ) -> Any:

        req = {
            "handle": handle,
            "mimeType": mime_type,
            "publicData": public_data,
        }

        if content is None and blocks is None:
            # Both none: empty file; to be imported later.
            upload_type = FileUploadType.NONE
        elif content is not None and blocks is not None:
            # Both not none: unclear what to do; raise an exception
            raise SteamshipError(
                message="Please provide only `blocks` or `content` to `File.create`."
            )
        elif blocks is not None:
            # Blocks
            upload_type = FileUploadType.BLOCKS
            req["blocks"] = [
                block.dict(by_alias=True, exclude_unset=True, exclude_none=True)
                for block in blocks or []
            ]

        elif content is not None:
            upload_type = FileUploadType.FILE
        else:
            raise Exception("Unable to determine upload type.")

        req["type"] = upload_type

        if tags:
            req["tags"] = [
                tag.dict(by_alias=True, exclude_unset=True, exclude_none=True) for tag in tags or []
            ]

        file_data = (
            ("file-part", content, "multipart/form-data")
            if upload_type == FileUploadType.FILE
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

        req = {
            "type": FileUploadType.FILE_IMPORTER,
            "url": url,
            "mimeType": mime_type,
            "pluginInstance": plugin_instance,
        }

        return client.post("file/create", payload=req, expect=File, as_background_task=True)

    def import_with_plugin(
        self,
        plugin_instance: str,
        url: str = None,
        mime_type: str = None,
    ) -> Task[File]:
        """Run an import operation on an (empty) file object that has already been created."""
        req = {
            "type": FileUploadType.FILE_IMPORTER,
            "id": self.id,
            "url": url,
            "mimeType": mime_type,
            "pluginInstance": plugin_instance,
        }

        return self.client.post("file/import", payload=req, expect=File, as_background_task=True)

    def refresh(self) -> File:
        refreshed = File.get(self.client, self.id)
        self.__init__(**refreshed.dict())
        self.client = refreshed.client
        for block in self.blocks:
            block.client = self.client
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

    @property
    def raw_data_url(self) -> Optional[str]:
        """Return a URL at which the data content of this File can be accessed.  If public_data is True,
        this content can be accessed without an API key.
        """
        if self.client is not None:
            return f"{self.client.config.api_base}file/{self.id}/raw"
        else:
            return None

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

    def generate(
        self,
        plugin_instance_handle: str,
        start_block_index: int = None,
        end_block_index: Optional[int] = None,
        block_index_list: Optional[List[int]] = None,
        append_output_to_file: bool = True,
        options: Optional[dict] = None,
        wait_on_tasks: List[Task] = None,
        make_output_public: bool = False,
    ) -> Task[GenerateResponse]:
        """Generate new content from this file. Assumes this file as context for input and output.  May specify start and end blocks."""
        from steamship.data.operations.generator import GenerateRequest, GenerateResponse

        if append_output_to_file:
            output_file_id = self.id
        else:
            output_file_id = None

        req = GenerateRequest(
            plugin_instance=plugin_instance_handle,
            input_file_id=self.id,
            input_file_start_block_index=start_block_index,
            input_file_end_block_index=end_block_index,
            input_file_block_index_list=block_index_list,
            append_output_to_file=append_output_to_file,
            output_file_id=output_file_id,
            options=options,
            make_output_public=make_output_public,
        )
        return self.client.post(
            "plugin/instance/generate", req, expect=GenerateResponse, wait_on_tasks=wait_on_tasks
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
    def list(
        client: Client,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
        sort_order: Optional[SortOrder] = SortOrder.DESC,
    ) -> ListFileResponse:
        return client.post(
            "file/list",
            ListFileRequest(pageSize=page_size, pageToken=page_token, sortOrder=sort_order),
            expect=ListFileResponse,
        )

    def append_block(
        self,
        text: str = None,
        tags: List[Tag] = None,
        content: Union[str, bytes] = None,
        url: Optional[str] = None,
        mime_type: Optional[MimeTypes] = None,
        public_data: bool = False,
    ) -> Block:
        """Append a new block to this File.  This is a convenience wrapper around
        Block.create(). You should provide only one of text, content, or url.

        This is a server-side operation, saving the new Block to the file. The new block
        is appended to this client-side File as well for convenience.
        """
        block = Block.create(
            self.client,
            file_id=self.id,
            text=text,
            tags=tags,
            content=content,
            url=url,
            mime_type=mime_type,
            public_data=public_data,
        )
        self.blocks.append(block)
        return block

    def set_public_data(self, public_data: bool):
        """Set the public_data flag on this File. If this object already exists server-side, update the flag."""
        self.public_data = public_data
        if self.client is not None and self.id is not None:
            req = {
                "id": self.id,
                "publicData": self.public_data,
            }
            return self.client.post("file/update", payload=req, expect=File)

    @staticmethod
    def from_local(
        client: Client,
        file_path: str,
        mime_type: MimeTypes = None,
        handle: str = None,
        tags: List[Tag] = None,
        public_data: bool = False,
    ) -> Any:
        """Loads a local file into a Steamship File.

        NOTE: the `file_path` should be relative to where the call to `from_local` is happening.

        Loaded files will automatically be tagged with a provenance tag.

        Args:
            client: Steamship client for the workspace
            file_path: Location of the file to upload **relative** to the current directory of the client
            mime_type: Optional specification of a particular mime type. If not provided, a guess will be made.
            handle: Intended handle (for lookups, etc.) for Steamship File
            tags: Metadata to add to the Steamship File
            public_data: Whether to make the Steamship File publicly-accessible
        """
        full_path = Path(file_path).resolve()

        if not mime_type:
            mime, _ = mimetypes.guess_type(file_path, strict=False)
            if MimeTypes.has_value(mime):
                mime_type = MimeTypes(mime)

        _tags = [
            Tag(kind=TagKind.PROVENANCE, name=ProvenanceTag.FILE, value={"file_path": file_path})
        ]

        if tags:
            _tags.extend(tags)

        with full_path.open("rb") as file:
            return File.create(
                client=client,
                content=file.read(),
                mime_type=mime_type,
                handle=handle,
                tags=_tags,
                public_data=public_data,
            )


class FileQueryResponse(Response):
    files: List[File]


ListFileResponse.update_forward_refs()
