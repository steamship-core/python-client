import io
import logging
import re
from dataclasses import dataclass
from typing import Tuple, Any, List

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
    """A file.
    """
    client: Client = None
    id: str = None
    handle: str = None
    mimeType: str = None
    spaceId: str = None
    corpusId: str = None
    blocks: [Block] = None
    tags: [Tag] = None
    filename: str = None

    @dataclass
    class CreateRequest:
        value: str = None
        data: str = None
        url: str = None
        filename: str = None
        type: str = None  # FileUploadType: fileImporter | value | url | data

        mimeType: str = None
        corpusId: str = None
        blocks: [Block.CreateRequest] = None
        tags: [Tag.CreateRequest] = None

        pluginInstance: str = None

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "File.CreateRequest":
            return File.CreateRequest(
                value=d.get('value', None),
                data=d.get('data', None),
                url=d.get('url', None),
                type=d.get('type', None),
                mimeType=d.get('mimeType', None),
                corpusId=d.get('corpusId', None),
                pluginInstance=d.get('pluginInstance', None),
                blocks=[Block.CreateRequest.from_dict(block, client=client) for block in d.get('blocks', [])],
                tags=[Tag.CreateRequest.from_dict(tag, client=client) for tag in d.get('tags', [])],
                filename=d.get('filename', None)
            )

        def to_dict(self) -> dict:
            return dict(
                value=self.value,
                data=self.data,
                url=self.url,
                type=self.type,
                mimeType=self.mimeType,
                corpusId=self.corpusId,
                pluginInstance=self.pluginInstance,
                blocks=[block.to_dict() for block in self.blocks] if self.blocks else [],
                tags=[tag.to_dict() for tag in self.tags] if self.tags else [],
                filename=self.filename
            )

    @dataclass
    class CreateResponse:
        data: Any = None
        mimeType: str = None

        def __init__(
                self,
                data: Any = None,
                string: str = None,
                bytes: io.BytesIO = None,
                json: io.BytesIO = None,
                mimeType: str = None
        ):
            data, mimeType, encoding = flexi_create(
                data=data,
                string=string,
                json=json,
                bytes=bytes,
                mimeType=mimeType
            )
            self.data = data
            self.mimeType = mimeType

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "File.CreateResponse":
            return File.CreateResponse(
                data=d.get('data', None),
                mimeType=d.get('mimeType', None)
            )

        def to_dict(self) -> dict:
            return dict(
                data=self.data,
                mimeType=self.mimeType
            )

    @dataclass
    class ListRequest(Request):
        corpusId: str = None

    @dataclass
    class ListResponse:
        files: List["File"]

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "File.ListResponse":
            return File.ListResponse(
                files=[File.from_dict(f, client=client) for f in d.get('files', [])]
            )

    @dataclass
    class RawRequest(Request):
        id: str

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "File":
        if d is None:
            return None
        if 'file' in d:
            d = d['file']
        return File(
            client=client,
            id=d.get('id', None),
            handle=d.get('handle', None),
            mimeType=d.get('mimeType', None),
            corpusId=d.get('corpusId', None),
            spaceId=d.get('spaceId', None),
            blocks=[Block.from_dict(block, client=client) for block in d.get('blocks', [])],
            tags=[Tag.from_dict(tag, client=client) for tag in d.get('tags', [])]
        )

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            handle=self.handle,
            mimeType=self.mimeType,
            corpusId=self.corpusId,
            spaceId=self.spaceId,
            blocks=[block.to_dict() for block in self.blocks] if self.blocks else [],
            tags=[tag.to_dict() for tag in self.tags] if self.tags else []
        )


    def delete(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> "Response[File]":
        return self.client.post(
            'file/delete',
            IdentifierRequest(id=self.id),
            expect=File,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def clear(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> Response[FileClearResponse]:
        return self.client.post(
            'file/clear',
            IdentifierRequest(id=self.id),
            expect=FileClearResponse,
            ifdQuery=self,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    @staticmethod
    def get(
            client: Client,
            id: str = None,
            handle: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> Response["File"]:
        return client.post(
            'file/get',
            IdentifierRequest(id=id, handle=handle),
            expect=File,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    @staticmethod
    def create(
            client: Client,
            filename: str = None,
            url: str = None,
            content: str = None,
            pluginInstance: str = None,
            mimeType: str = None,
            blocks: List[Block.CreateRequest] = None,
            tags: List[Tag.CreateRequest] = None,
            corpusId: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> "Response[File]":

        if filename is None and content is None and url is None and pluginInstance is None and blocks is None:
            raise Exception("Either filename, content, url, or plugin Instance must be provided.")

        uploadType = None
        if blocks is not None:
            uploadType = FileUploadType.blocks
        elif pluginInstance is not None:
            uploadType = FileUploadType.fileImporter
        elif content is not None:
            # We're still going to use the file upload method for file uploads
            uploadType = FileUploadType.file
        elif filename is not None:
            with open(filename, 'rb') as f:
                content = f.read()
            uploadType = FileUploadType.file
        else:
            if url is not None:
                raise Exception("Unable to determine upload type. For scraping a URL, use the File.scrape method.")
            else:
                raise Exception("Unable to determine upload type.")

        req = File.CreateRequest(
            type=uploadType,
            corpusId=corpusId,
            url=url,
            mimeType=mimeType,
            pluginInstance=pluginInstance,
            blocks=blocks,
            tags=tags,
            filename=filename
        )

        # Defaulting this here, as opposed to in the Engine, because it is processed by Vapor
        filePartName = filename if filename else "unnamed"
        return client.post(
            'file/create',
            payload=req,
            file=(filePartName, content, "multipart/form-data") if uploadType != FileUploadType.blocks else None,
            expect=File,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    @staticmethod
    def list(
            client: Client,
            corpusId: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ):
        req = File.ListRequest(
            corpusId=corpusId
        )
        res = client.post(
            'file/list',
            payload=req,
            expect=File.ListResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )
        return res

    @staticmethod
    def scrape(
            client: Client,
            url: str,
            corpusId: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> "File":
        req = File.CreateRequest(
            type=FileUploadType.url,
            url=url,
            corpusId=corpusId
        )

        return client.post(
            'file/create',
            payload=req,
            expect=File,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def refresh(self):
        return File.get(self.client, self.id)

    def query(
            self,
            tagFilterQuery: str,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> Response["FileQueryResponse"]:

        req = FileQueryRequest(
            tagFilterQuery=tagFilterQuery
        )
        res = self.client.post(
            'file/query',
            payload=req,
            expect=FileQueryResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )
        return res

    def raw(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None):
        req = File.RawRequest(
            id=self.id,
        )

        return self.client.post(
            'file/raw',
            payload=req,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space,
            rawResponse=True
        )


@dataclass
class FileQueryResponse:
    files: List[File]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "FileQueryResponse":
        return FileQueryResponse(
            files=[File.from_dict(file, client=client) for file in d.get('files', None)]
        )