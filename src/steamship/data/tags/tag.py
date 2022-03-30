import json
from dataclasses import dataclass
from typing import List, Any

from steamship.base import Client, Request, Response


@dataclass
class Tag:
    client: Client = None
    id: str = None
    fileId: str = None
    blockId: str = None
    kind: str = None  # E.g. ner
    name: str = None  # E.g. person
    value: str = None  # JSON Metadata
    startIdx: int = None  # w/r/t block.text. None means 0 if blockId is not None
    endIdx: int = None  # w/r/t block.text. None means -1 if blockId is not None

    @dataclass
    class CreateRequest(Request):
        id: str = None
        fileId: str = None
        blockId: str = None
        kind: str = None
        name: str = None
        startIdx: int = None
        endIdx: int = None
        value: Any = None
        upsert: bool = None

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "Tag.CreateRequest":
            return Tag.CreateRequest(
                id=d.get('id', None),
                fileId=d.get('fileId', None),
                blockId=d.get('blockId', None),
                kind=d.get('kind', None),
                name=d.get('name', None),
                startIdx=d.get('startIdx', None),
                endIdx=d.get('endIdx', None),
                value=d.get('value', None),
                upsert=d.get('upsert', None),
            )

    @dataclass
    class DeleteRequest(Request):
        id: str = None
        fileId: str = None
        blockId: str = None

    @dataclass
    class ListRequest(Request):
        fileId: str = None
        blockId: str = None

    @dataclass
    class ListResponse(Request):
        tags: List["Tag"] = None

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "Tag.ListResponse":
            if d is None:
                return None
            return Tag.ListResponse(
                tags=[Tag.from_dict(x, client=client) for x in (d.get("tags", []) or [])]
            )

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "Tag":
        return Tag(
            client=client,
            id=d.get('id', None),
            fileId=d.get('fileId', None),
            blockId=d.get('blockId', None),
            kind=d.get('kind', None),
            name=d.get('name', None),
            startIdx=d.get('startIdx', None),
            endIdx=d.get('endIdx', None),
            value=d.get('value', None)
        )

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            fileId=self.fileId,
            blockId=self.blockId,
            kind=self.kind,
            name=self.name,
            startIdx=self.startIdx,
            endIdx=self.endIdx,
            value=self.value
        )

    @staticmethod
    def create(
            client: Client,
            fileId: str = None,
            blockId: str = None,
            kind: str = None,
            name: str = None,
            startIdx: int = None,
            endIdx: int = None,
            value: Any = None,
            upsert: bool = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response["Tag"]:
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value)

        req = Tag.CreateRequest(
            fileId=fileId,
            blockId=blockId,
            kind=kind,
            name=name,
            startIdx=startIdx,
            endIdx=endIdx,
            value=value,
            upsert=upsert
        )
        return client.post(
            'tag/create',
            req,
            expect=Tag,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    @staticmethod
    def listPublic(
            client: Client,
            fileId: str = None,
            blockId: str = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response["Tag.ListResponse"]:
        return client.post(
            'tag/list',
            Tag.ListRequest(
                fileId=fileId,
                blockId=blockId
            ),
            expect=Tag.ListResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    def delete(self) -> Response["Tag"]:
        return self.client.post(
            'tag/delete',
            Tag.DeleteRequest(id=self.id, fileId=self.fileId, blockId=self.blockId),
            expect=Tag,
        )
