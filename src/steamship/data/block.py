from dataclasses import dataclass
from typing import Any, List, Optional, Union

from steamship.base import Client, Request, Response
from steamship.base.request import IdentifierRequest
from steamship.data.tags.tag import Tag


@dataclass
class BlockQueryRequest(Request):
    tagFilterQuery: str


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

        # noinspection PyUnusedLocal
        @staticmethod
        def from_dict(d: Any, client: Client = None) -> "Block.CreateRequest":
            return Block.CreateRequest(
                id=d.get("id"),
                fileId=d.get("fileId"),
                text=d.get("text"),
                tags=[Tag.CreateRequest.from_dict(tag) for tag in d.get("tags", [])],
                upsert=d.get("upsert"),
            )

        def to_dict(self) -> dict:
            return dict(
                id=self.id,
                fileId=self.fileId,
                text=self.text,
                upsert=self.upsert,
                tags=[tag.to_dict() for tag in self.tags]
                if self.tags
                else [],  # TODO (enias): Deprecate
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
        def from_dict(d: Any, client: Client = None) -> "Optional[Block.ListResponse]":
            if d is None:
                return None
            return Block.ListResponse(
                blocks=[Block.from_dict(x, client=client) for x in (d.get("blocks", []) or [])]
            )

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> Union["Block", None]:
        if d is None:
            return None
        return Block(
            client=client,
            id=d.get("id"),
            fileId=d.get("fileId"),
            text=d.get("text"),
            tags=list(map(lambda tag: Tag.from_dict(tag, client=client), d.get("tags", []) or [])),
        )

    def to_dict(self) -> dict:
        tags = None
        if self.tags is not None:
            tags = [tag.to_dict() for tag in self.tags]

        return dict(id=self.id, fileId=self.fileId, text=self.text, tags=tags)

    @staticmethod
    def get(
        client: Client,
        _id: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response["Block"]:
        return client.post(
            "block/get",
            IdentifierRequest(id=_id),
            expect=Block,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    @staticmethod
    def create(
        client: Client,
        file_id: str = None,
        text: str = None,
        tags: List[Tag.CreateRequest] = None,
        upsert: bool = None,
        space_id: str = None,
        space_handle: str = None,
    ) -> Response["Block"]:
        req = Block.CreateRequest(fileId=file_id, text=text, tags=tags, upsert=upsert)
        return client.post(
            "block/create",
            req,
            expect=Block,
            space_id=space_id,
            space_handle=space_handle,
        )

    @staticmethod
    def list_public(
        client: Client,
        file_id: str = None,
        space_id: str = None,
        space_handle: str = None,
    ) -> Response["Block.ListResponse"]:
        return client.post(
            "block/list",
            Block.ListRequest(fileId=file_id),
            expect=Block.ListResponse,
            space_id=space_id,
            space_handle=space_handle,
        )

    def delete(self) -> Response["Block"]:
        return self.client.post(
            "block/delete",
            Block.DeleteRequest(id=self.id),
            expect=Tag,
        )

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response["BlockQueryResponse"]:
        # TODO: Is this a static method?
        req = BlockQueryRequest(tagFilterQuery=tag_filter_query)
        res = client.post(
            "block/query",
            payload=req,
            expect=BlockQueryResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )
        return res


@dataclass
class BlockQueryResponse:
    blocks: List[Block]

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "BlockQueryResponse":
        return BlockQueryResponse(
            blocks=[Block.from_dict(block, client=client) for block in d.get("blocks", [])]
        )
