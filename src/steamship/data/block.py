from __future__ import annotations

from typing import Any, List, Optional

from steamship.base import Client, Request, Response
from steamship.base.configuration import CamelModel
from steamship.base.request import IdentifierRequest
from steamship.data.tags.tag import Tag


class BlockQueryRequest(Request):
    tag_filter_query: str


class Block(CamelModel):
    client: Client = None
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

    class DeleteRequest(Request):
        id: str = None

    class ListRequest(Request):
        file_id: str = None

    class ListResponse(Response):
        blocks: List[Block] = []

    @staticmethod
    def get(
        client: Client,
        _id: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[Block]:
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
    ) -> Response[Block]:
        req = Block.CreateRequest(file_id=file_id, text=text, tags=tags, upsert=upsert)
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
    ) -> Response[Block.ListResponse]:
        return client.post(
            "block/list",
            Block.ListRequest(file_id=file_id),
            expect=Block.ListResponse,
            space_id=space_id,
            space_handle=space_handle,
        )

    def delete(self) -> Response[Block]:
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
    ) -> Response[BlockQueryResponse]:
        # TODO: Is this a static method?
        req = BlockQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "block/query",
            payload=req,
            expect=BlockQueryResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )
        return res


class BlockQueryResponse(Response):
    blocks: List[Block]


Block.ListResponse.update_forward_refs()
Block.update_forward_refs()
