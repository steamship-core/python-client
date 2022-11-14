from __future__ import annotations

import json
from typing import Any, Dict, List

from pydantic import Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import Request
from steamship.base.response import Response


class TagQueryRequest(Request):
    tag_filter_query: str


class Tag(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    file_id: str = None
    block_id: str = None
    kind: str = None  # E.g. ner
    name: str = None  # E.g. person
    value: Dict[str, Any] = None  # JSON Metadata
    start_idx: int = None  # w/r/t block.text. None means 0 if blockId is not None
    end_idx: int = None  # w/r/t block.text. None means -1 if blockId is not None

    class CreateRequest(Request):
        id: str = None
        file_id: str = None
        block_id: str = None
        kind: str = None
        name: str = None
        start_idx: int = None
        end_idx: int = None
        value: Dict[str, Any] = None

    class DeleteRequest(Request):
        id: str = None
        file_id: str = None
        block_id: str = None

    class ListRequest(Request):
        file_id: str = None
        block_id: str = None

    class ListResponse(Response):
        tags: List[Tag] = None

    @staticmethod
    def create(
        client: Client,
        file_id: str = None,
        block_id: str = None,
        kind: str = None,
        name: str = None,
        start_idx: int = None,
        end_idx: int = None,
        value: Dict[str, Any] = None,
    ) -> Tag:
        req = Tag.CreateRequest(
            file_id=file_id,
            block_id=block_id,
            kind=kind,
            name=name,
            start_idx=start_idx,
            end_idx=end_idx,
            value=value,
        )
        return client.post("tag/create", req, expect=Tag)

    def delete(self) -> Tag:
        return self.client.post(
            "tag/delete",
            Tag.DeleteRequest(id=self.id, file_id=self.file_id, block_id=self.block_id),
            expect=Tag,
        )

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
    ) -> TagQueryResponse:
        req = TagQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "tag/query",
            payload=req,
            expect=TagQueryResponse,
        )
        return res


class TagQueryResponse(Response):
    tags: List[Tag]


Tag.ListResponse.update_forward_refs()
