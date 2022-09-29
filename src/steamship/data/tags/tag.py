from __future__ import annotations

import json
from typing import Any, Dict, List

from steamship.base import Client, Request, Response
from steamship.base.configuration import CamelModel


class TagQueryRequest(Request):
    tag_filter_query: str


class Tag(CamelModel):
    client: Client = None
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
        upsert: bool = None

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
        value: Any = None,
        upsert: bool = None,
        space_id: str = None,
        space_handle: str = None,
    ) -> Response[Tag]:
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value)

        req = Tag.CreateRequest(
            file_id=file_id,
            block_id=block_id,
            kind=kind,
            name=name,
            start_idx=start_idx,
            end_idx=end_idx,
            value=value,
            upsert=upsert,
        )
        return client.post(
            "tag/create", req, expect=Tag, space_id=space_id, space_handle=space_handle
        )

    @staticmethod
    def list_public(
        client: Client,
        file_id: str = None,
        block_id: str = None,
        space_id: str = None,
        space_handle: str = None,
    ) -> Response[Tag.ListResponse]:
        return client.post(
            "tag/list",
            Tag.ListRequest(file_id=file_id, block_id=block_id),
            expect=Tag.ListResponse,
            space_id=space_id,
            space_handle=space_handle,
        )

    def delete(self) -> Response[Tag]:
        return self.client.post(
            "tag/delete",
            Tag.DeleteRequest(id=self.id, file_id=self.file_id, block_id=self.block_id),
            expect=Tag,
        )

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[TagQueryResponse]:
        req = TagQueryRequest(tag_filter_query=tag_filter_query)
        res = client.post(
            "tag/query",
            payload=req,
            expect=TagQueryResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )
        return res


class TagQueryResponse(Response):
    tags: List[Tag]


Tag.ListResponse.update_forward_refs()
