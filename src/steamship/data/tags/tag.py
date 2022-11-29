from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import Request
from steamship.base.response import Response


class TagQueryRequest(Request):
    tag_filter_query: str


class Tag(CamelModel):
    # Steamship client.
    client: Client = Field(None, exclude=True)

    # ID of the tag in the database.
    id: str = None

    # ID of the file associated with the tag.
    file_id: str = None

    # ID of the block associated with the tag. If not None, `start_idx` and `end_idx` should be set.
    block_id: Optional[str] = None

    # The kind of tag. See the ``TagKind`` enum class for suggestions.
    kind: str = None  # E.g. ner

    # The name of tag. See the ``DocTag``, ``TokenTag``, etc enum classes for suggestions.
    name: Optional[str] = None  # E.g. person

    # The value payload of the tag. Always a JSON-style object.
    value: Optional[Dict[str, Any]] = None

    # Character index in associated block of the start of the span of text this tag comments upon. Start-inclusive.
    start_idx: Optional[int] = None

    # Character index in associated block of the end of the span of text this tag comments upon. End-exclusive.
    end_idx: Optional[int] = None

    # The text covered by the tag.
    # Note:
    #   The text will not always be materialized into the tag object
    #   itself; you may have to fetch it with file.text[tag.start_idx:tag.end_idx]
    # Note:
    #   Changing this field will not result in changes to Steamship's database.
    #   TODO(ted): Consider refactoring as a read-only property.
    #
    text: Optional[str] = None

    class CreateRequest(Request):
        """Request to create a new Tag."""

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

    def index(self, plugin_instance: Any = None):
        """Index this tag."""
        return plugin_instance.insert(self)

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

    # @staticmethod
    # def search(
    #     client: Client,
    #     search_index: Any,
    # ) -> TagQueryResponse:
    #     # Avoid the circular import.
    #     from steamship.data.plugin.index_plugin_instance import EmbeddingIndexPluginInstance
    #
    #     if not isinstance(search_index, EmbeddingIndexPluginInstance):
    #         raise SteamshipError(message="The search_index field")
    #
    #
    #     req = TagQueryRequest(tag_filter_query=tag_filter_query)
    #     res = client.post(
    #         "tag/query",
    #         payload=req,
    #         expect=TagQueryResponse,
    #     )
    #     return res


class TagQueryResponse(Response):
    tags: List[Tag]


Tag.ListResponse.update_forward_refs()
