from __future__ import annotations

from typing import Any, List, Optional

from pydantic import Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import DeleteRequest, IdentifierRequest, Request
from steamship.base.response import Response
from steamship.data.tags.tag import Tag


class BlockQueryRequest(Request):
    tag_filter_query: str


class Block(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    file_id: str = None
    text: str = None
    tags: Optional[List[Tag]] = []

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
        tags: List[Tag] = None,
    ) -> Block:
        req = Block(file_id=file_id, text=text, tags=tags)
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
        req = BlockQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "block/query",
            payload=req,
            expect=BlockQueryResponse,
        )
        return res

    def index(self, embedding_plugin_instance: Any = None):
        """Index this block."""
        tags = [
            Tag(
                text=self.text,
                file_id=self.file_id,
                block_id=self.id,
                kind="block",
                start_idx=0,
                end_idx=len(self.text),
            )
        ]
        return embedding_plugin_instance.insert(tags)


class BlockQueryResponse(Response):
    blocks: List[Block]


Block.ListResponse.update_forward_refs()
Block.update_forward_refs()
