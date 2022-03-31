from dataclasses import dataclass
from typing import List, Union

from steamship.base import Client, Request, Response
from steamship.base.request import IdentifierRequest
from steamship.data.tags.tag import Tag


@dataclass
class Block:
    client: Client = None
    id: str = None
    fileId: str = None
    text: str = None
    tags: List[Tag] = None

    @dataclass
    class CreateRequest(Request):
        id: str = None
        fileId: str = None
        text: str = None
        tags: List[Tag.CreateRequest] = None
        upsert: bool = None

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "Block.CreateRequest":
            return Block.CreateRequest(
                id=d.get('id', None),
                fileId=d.get('fileId', None),
                text=d.get('text', None),
                tags=[Tag.CreateRequest.from_dict(tag, client=client) for tag in d.get("tags", [])],
                upsert=d.get('upsert', None),
            )

        def to_dict(self)-> dict:
            return dict(
                id=self.id,
                fileId=self.fileId,
                text=self.text,
                upsert=self.upsert,
                tags=[tag.to_dict() for tag in self.tags] if self.tags else []
            )

    @dataclass
    class DeleteRequest(Request):
        id: str = None

    @dataclass
    class ListRequest(Request):
        fileId: str = None

    @dataclass
    class ListResponse(Request):
        blocks: List["Block"] = None

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "Block.ListResponse":
            if d is None:
                return None
            return Block.ListResponse(
                blocks=[Block.from_dict(x, client=client) for x in (d.get("blocks", []) or [])]
            )

    @staticmethod
    def from_dict(d: any, client: Client = None) -> Union["Block", None]:
        if d is None:
            return None
        return Block(
            client=client,
            id=d.get('id', None),
            fileId=d.get('fileId', None),
            text=d.get('text', None),
            tags=list(map(lambda tag: Tag.from_dict(tag, client=client), d.get('tags', [])))
        )

    def to_dict(self) -> dict:
        tags = None
        if self.tags is not None:
            tags = [tag.to_dict() for tag in self.tags]

        return dict(
            id=self.id,
            fileId=self.fileId,
            text=self.text,
            tags=tags
        )

    @staticmethod
    def get(
            client: Client,
            id: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> Response["Block"]:
        return client.post(
            'block/get',
            IdentifierRequest(id=id),
            expect=Block,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    @staticmethod
    def create(
            client: Client,
            fileId: str = None,
            text: str = None,
            tags: List[Tag.CreateRequest] = None,
            upsert: bool = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response["Block"]:
        req = Block.CreateRequest(
            fileId=fileId,
            text=text,
            tags=tags,
            upsert=upsert
        )
        return client.post(
            'block/create',
            req,
            expect=Block,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    @staticmethod
    def listPublic(
            client: Client,
            fileId: str = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response["Block.ListResponse"]:
        return client.post(
            'block/list',
            Block.ListRequest(
                fileId=fileId
            ),
            expect=Block.ListResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    def delete(self) -> Response["Block"]:
        return self.client.post(
            'block/delete',
            Block.DeleteRequest(id=self.id),
            expect=Tag,
        )
