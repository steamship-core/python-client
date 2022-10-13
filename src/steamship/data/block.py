from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from steamship.base import Client, DeleteRequest, IdentifierRequest, Request, Response
from steamship.base.configuration import CamelModel
from steamship.data.tags.tag import Tag


class BlockQueryRequest(Request):
    tag_filter_query: str


class Block(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    file_id: str = None
    text: str = None
    tags: Optional[List[Tag]] = []

    class CreateRequest(Request):
        id: str = None
        file_id: str = None
        text: str = None
        tags: Optional[List[Tag.CreateRequest]] = []
        upsert: bool = None

    class ListRequest(Request):
        file_id: str = None

    class ListResponse(Response):
        blocks: List[Block] = []

    @staticmethod
    def get(
        client: Client,
        _id: str = None,
    ) -> Block:
        return client.post(
            "block/get",
            IdentifierRequest(id=_id),
            expect=Block,
        )

    @staticmethod
    def create(
        client: Client,
        file_id: str = None,
        text: str = None,
        tags: List[Tag.CreateRequest] = None,
        upsert: bool = None,
    ) -> Block:
        req = Block.CreateRequest(file_id=file_id, text=text, tags=tags, upsert=upsert)
        return client.post(
            "block/create",
            req,
            expect=Block,
        )

    def delete(self) -> Block:
        return self.client.post(
            "block/delete",
            DeleteRequest(id=self.id),
            expect=Tag,
        )

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
    ) -> BlockQueryResponse:
        # TODO: Is this a static method?
        req = BlockQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "block/query",
            payload=req,
            expect=BlockQueryResponse,
        )
        return res


class BlockQueryResponse(Response):
    blocks: List[Block]


Block.ListResponse.update_forward_refs()
Block.update_forward_refs()
