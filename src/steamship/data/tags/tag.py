import json
from dataclasses import dataclass
from typing import Any, List, Optional, Dict

from steamship.base import Client, Request, Response


@dataclass
class TagQueryRequest(Request):
    tagFilterQuery: str


@dataclass
class Tag:  # TODO (enias): Make pep8 compatible
    client: Client = None
    id: str = None
    fileId: str = None
    blockId: str = None
    kind: str = None  # E.g. ner
    name: str = None  # E.g. person
    value: Dict[str, Any] = None  # JSON Metadata
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
        value: Dict[str, Any] = None
        upsert: bool = None

        # noinspection PyUnusedLocal
        @staticmethod
        def from_dict(d: Any, client: Client = None) -> "Tag.CreateRequest":
            return Tag.CreateRequest(
                id=d.get("id"),
                fileId=d.get("fileId"),
                blockId=d.get("blockId"),
                kind=d.get("kind"),
                name=d.get("name"),
                startIdx=d.get("startIdx"),
                endIdx=d.get("endIdx"),
                value=d.get("value"),
                upsert=d.get("upsert"),
            )

        def to_dict(self):
            return dict(
                id=self.id,
                fileId=self.fileId,
                blockId=self.blockId,
                kind=self.kind,
                name=self.name,
                startIdx=self.startIdx,
                endIdx=self.endIdx,
                value=self.value,
                upsert=self.upsert,
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
        def from_dict(d: Any, client: Client = None) -> "Optional[Tag.ListResponse]":
            if d is None:
                return None
            return Tag.ListResponse(
                tags=[
                    Tag.from_dict(x, client=client) for x in (d.get("tags", []) or [])
                ]
            )

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "Tag":
        return Tag(
            client=client,
            id=d.get("id"),
            fileId=d.get("fileId"),
            blockId=d.get("blockId"),
            kind=d.get("kind"),
            name=d.get("name"),
            startIdx=d.get("startIdx"),
            endIdx=d.get("endIdx"),
            value=d.get("value"),
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
            value=self.value,
        )

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
    ) -> Response["Tag"]:
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value)

        req = Tag.CreateRequest(
            fileId=file_id,
            blockId=block_id,
            kind=kind,
            name=name,
            startIdx=start_idx,
            endIdx=end_idx,
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
    ) -> Response["Tag.ListResponse"]:
        return client.post(
            "tag/list",
            Tag.ListRequest(fileId=file_id, blockId=block_id),
            expect=Tag.ListResponse,
            space_id=space_id,
            space_handle=space_handle,
        )

    def delete(self) -> Response["Tag"]:
        return self.client.post(
            "tag/delete",
            Tag.DeleteRequest(id=self.id, fileId=self.fileId, blockId=self.blockId),
            expect=Tag,
        )

    @staticmethod
    def query(
        client: Client,
        tag_filter_query: str,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response["TagQueryResponse"]:

        req = TagQueryRequest(tagFilterQuery=tag_filter_query)
        res = client.post(
            "tag/query",
            payload=req,
            expect=TagQueryResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )
        return res


@dataclass
class TagQueryResponse:
    tags: List[Tag]

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "TagQueryResponse":
        return TagQueryResponse(
            tags=[Tag.from_dict(tag, client=client) for tag in d.get("tags", [])]
        )
