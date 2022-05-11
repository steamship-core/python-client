import io
import logging
from dataclasses import dataclass
from typing import Any, List, Union, Optional

from pydantic import BaseModel

from steamship.base import Client, Response, Request
from steamship.base.binary_utils import flexi_create
from steamship.base.request import IdentifierRequest
from steamship.data.block import Block
from steamship.data.tags import Tag


class FileUploadType:
    file = "file"  # The CreateRequest contains a file upload that should be used
    url = "url"  # The CreateRequest contains a url that should be scraped
    value = "value"  # The Create Request contains a `text` field that should be used
    fileImporter = "fileImporter"  # The CreateRequest contains a fileImporter handle that should be used
    blocks = "blocks"  # The CreateRequest contains blocks and tags that should be read in directly


_logger = logging.getLogger(__name__)


@dataclass
class FileClearResponse:
    id: str


@dataclass
class FileQueryRequest(Request):
    tagFilterQuery: str


@dataclass
class File:
    """A file."""

    client: Client = None
    id: str = None
    handle: str = None
    mime_type: str = None
    space_id: str = None
    corpus_id: str = None
    blocks: List[Block] = None
    tags: List[Tag] = None
    filename: str = None

    class CreateRequest(BaseModel, Request):
        value: str = None
        data: str = None
        url: str = None
        filename: str = None
        type: str = None  # FileUploadType: fileImporter | value | url | data
        mimeType: str = None  # TODO: This should work
        corpusId: str = None
        blocks: List[Block.CreateRequest] = None
        tags: List[Tag.CreateRequest] = None
        pluginInstance: str = None

        # @staticmethod
        # def from_dict(d: Any, client: Client = None) -> "File.CreateRequest":
        #     logging.info("Calling from_dict on the File!")
        #     return File.CreateRequest.parse_obj(d)

        # def to_dict(self) -> dict:
        #     logging.info("Calling to_dict on the File!")
        #     return self.dict(exclude_unset=False, exclude_defaults=False, exclude_none=False)

    @dataclass
    class CreateResponse:
        data: Any = None
        mimeType: str = None

        def __init__(
            self,
            data: Any = None,
            string: str = None,
            bytes: Union[bytes, io.BytesIO] = None,
            json: io.BytesIO = None,
            mime_type: str = None,
        ):
            data, mime_type, encoding = flexi_create(
                data=data, string=string, json=json, bytes=bytes, mime_type=mime_type
            )
            self.data = data
            self.mimeType = mime_type

        # noinspection PyUnusedLocal
        @staticmethod
        def from_dict(d: Any, client: Client = None) -> "File.CreateResponse":
            return File.CreateResponse(
                data=d.get("data", None), mime_type=d.get("mimeType", None)
            )

        def to_dict(self) -> dict:
            return dict(data=self.data, mimeType=self.mimeType)

    @dataclass
    class ListRequest(Request):
        corpusId: str = None

    @dataclass
    class ListResponse:
        files: List["File"]

        @staticmethod
        def from_dict(d: Any, client: Client = None) -> "File.ListResponse":
            return File.ListResponse(
                files=[File.from_dict(f, client=client) for f in d.get("files", [])]
            )

    @dataclass
    class RawRequest(Request):
        id: str

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "Optional[File]":
        # TODO (enias): Resolve code duplication
        if d is None:
            return None
        if "file" in d:
            d = d["file"]
        return File(
            client=client,
            id=d.get("id"),
            handle=d.get("handle"),
            mime_type=d.get("mimeType"),
            corpus_id=d.get("corpusId"),
            space_id=d.get("spaceId"),
            blocks=[
                Block.from_dict(block, client=client) for block in d.get("blocks", [])
            ],
            tags=[Tag.from_dict(tag, client=client) for tag in d.get("tags", [])],
        )

    def to_dict(self) -> dict:
        # TODO (enias): Resolve code duplication
        return dict(
            id=self.id,
            handle=self.handle,
            mimeType=self.mime_type,
            corpusId=self.corpus_id,
            spaceId=self.space_id,
            blocks=[block.to_dict() for block in self.blocks] if self.blocks else [],
            tags=[tag.to_dict() for tag in self.tags] if self.tags else [],
        )

    def delete(
        self, space_id: str = None, space_handle: str = None, space: Any = None
    ) -> "Response[File]":
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
            id_query=self,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    @staticmethod
    def get(
        client: Client,
        id: str = None,
        handle: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response["File"]:  # TODO (Enias): Why is this a staticmethod?
        return client.post(
            "file/get",
            IdentifierRequest(id=id, handle=handle),
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
    ) -> "Response[File]":

        if (
            filename is None
            and content is None
            and url is None
            and plugin_instance is None
            and blocks is None
        ):
            raise Exception(
                "Either filename, content, url, or plugin Instance must be provided."
            )

        if blocks is not None:
            upload_type = FileUploadType.blocks
        elif plugin_instance is not None:
            upload_type = FileUploadType.fileImporter
        elif content is not None:
            # We're still going to use the file upload method for file uploads
            upload_type = FileUploadType.file
        elif filename is not None:
            with open(filename, "rb") as f:
                content = f.read()
            upload_type = FileUploadType.file
        else:
            if url is not None:
                raise Exception(
                    "Unable to determine upload type. For scraping a URL, use the File.scrape method."
                )
            else:
                raise Exception("Unable to determine upload type.")

        req = File.CreateRequest(
            type=upload_type,
            corpusId=corpus_id,
            url=url,
            mimeType=mime_type,
            pluginInstance=plugin_instance,
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
            if upload_type != FileUploadType.blocks
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

    @staticmethod
    def scrape(
        client: Client,
        url: str,
        corpus_id: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> "Response[File]":
        req = File.CreateRequest(type=FileUploadType.url, url=url, corpusId=corpus_id)

        return client.post(
            "file/create",
            payload=req,
            expect=File,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def refresh(self):
        return File.get(self.client, self.id)

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response["FileQueryResponse"]:

        req = FileQueryRequest(tagFilterQuery=tag_filter_query)
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

        return self.client.post(
            "file/raw",
            payload=req,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
            raw_response=True,
        )

    @staticmethod
    def upload(
        client: Client,
        filename: str = None,
        content: str = None,
        mime_type: str = None,
        corpus_id: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> "Response[File]":
        pass

    def blockify(self, plugin_instance: str = None):
        pass

    def tag(
        self,
        plugin_instance: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ):
        pass


@dataclass
class FileQueryResponse:
    files: List[File]

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "FileQueryResponse":
        return FileQueryResponse(
            files=[File.from_dict(file, client=client) for file in d.get("files", [])]
        )
