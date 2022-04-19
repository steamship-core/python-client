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


class File:
    pass


class FileUploadType:
    file = "file"  # The CreateRequest contains a file upload that should be used
    url = "url"  # The CreateRequest contains a url that should be scraped
    value = "value"  # The Create Request contains a `text` field that should be used
    fileImporter = "fileImporter"  # The CreateRequest contains a fileImporter handle that should be used
    blocks = "blocks"  # The CreateRequest contains blocks and tags that should be read in directly


_logger = logging.getLogger(__name__)


def parseDquery(query: str) -> List[Tuple[str, str, str]]:
    query = re.sub(' +', ' ', query.strip())
    parts = re.split(r'\s*(?=[@#])', query)
    ret = []

    for s in parts:
        s = s.strip()
        if not s:
            continue

        command = ''
        if s[0] in ['@', '#']:
            command = s[0]
            s = s[1:]

        if command == '':
            ret.append((command, None, s))
            continue

        if '"' not in s and ":" not in s:
            if command == '#':
                ret.append((command, 'contains', s))
            else:
                ret.append((command, s, None))
            continue

        modifier = None
        if ':' in s:
            ss = s.split(':')
            modifier = ss[0]
            s = ss[1]

        content = s
        if '"' in s:
            i = s.index('"')
            content = s[1 + i:-1]
            if modifier is None:
                s = s[:i]
                modifier = s
                if modifier == '':
                    modifier = None

        ret.append((command, modifier, content))
    return ret


@dataclass
class FileClearResponse:
    id: str


@dataclass
class SpanQuery:
    text: str = None
    label: str = None
    spanType: str = None


@dataclass
class FileQueryRequest(Request):
    fileId: str
    type: str = None
    hasSpans: List[SpanQuery] = None
    text: str = None
    textMode: str = None
    isQuote: bool = None


@dataclass
class FileQueryResponse:
    id: str
    blocks: List[Block]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "FileQueryResponse":
        return FileQueryResponse(
            id=d.get('id', None),
            blocks=[Block.from_dict(block, client=client) for block in d.get('blocks', None)]
        )


@dataclass
class File:
    """A file.
    """
    client: Client = None
    id: str = None
    name: str = None
    handle: str = None
    mimeType: str = None
    spaceId: str = None
    corpusId: str = None
    blocks: [Block] = None
    tags: [Tag] = None

    @dataclass
    class CreateRequest:
        value: str = None
        data: str = None
        url: str = None
        type: str = None  # FileUploadType: fileImporter | value | url | data

        mimeType: str = None
        corpusId: str = None
        name: str = None
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
                name=d.get('name', None),
                blocks=[Block.CreateRequest.from_dict(block, client=client) for block in d.get('blocks', [])],
                tags=[Tag.CreateRequest.from_dict(tag, client=client) for tag in d.get('tags', [])]
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
                name=self.name,
                blocks=[block.to_dict() for block in self.blocks] if self.blocks else []
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
            data, mimeType = flexi_create(
                body=data,
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
            name=d.get('name', None),
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
            name= self.name,
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
            name: str = None,
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

        if filename is None and name is None and content is None and url is None and pluginInstance is None and blocks is None:
            raise Exception("Either filename, name + content, url, or plugin Instance must be provided.")

        uploadType = None
        if blocks is not None:
            uploadType = FileUploadType.blocks
        elif pluginInstance is not None:
            uploadType = FileUploadType.fileImporter
        elif content is not None:
            # We're still goign to use the file upload method for file uploads
            uploadType = FileUploadType.file
        elif filename is not None:
            with open(filename, 'rb') as f:
                content = f.read()
                name = filename
            uploadType = FileUploadType.file
        else:
            if url is not None:
                raise Exception("Unable to determine upload type. For scraping a URL, use the File.scrape method.")
            else:
                raise Exception("Unable to determine upload type.")

        req = File.CreateRequest(
            type=uploadType,
            corpusId=corpusId,
            name=name,
            url=url,
            mimeType=mimeType,
            pluginInstance=pluginInstance,
            blocks=blocks,
            tags=tags
        )

        return client.post(
            'file/create',
            payload=req,
            file=(name, content, "multipart/form-data") if uploadType != FileUploadType.blocks else None,
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
            name: str = None,
            corpusId: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> "File":
        if name is None:
            name = url
        req = File.CreateRequest(
            type=FileUploadType.url,
            name=name,
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

    def dquery(
            self,
            dQuery: str,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None):
        blockType = None
        hasSpans = []
        text = None
        isQuote = None
        textMode = None

        for tup in parseDquery(dQuery):
            (cmd, subcmd, content) = tup
            if cmd == '':
                blockType = content
            elif cmd == '#':
                text = content
                textMode = subcmd
            elif cmd == '@':
                hasSpans.append(SpanQuery(label=subcmd, text=content))

        return self.query(
            blockType=blockType,
            hasSpans=hasSpans,
            text=text,
            textMode=textMode,
            isQuote=isQuote,
            pd=True,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def query(
            self,
            hasSpans: List[SpanQuery] = None,
            text: str = None,
            textMode: str = None,
            isQuote: bool = None,
            pd: bool = False,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> Response[FileQueryResponse]:

        req = FileQueryRequest(
            fileId=self.id,
            hasSpans=hasSpans,
            text=text,
            textMode=textMode,
            isQuote=isQuote
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
