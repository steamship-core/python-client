from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field

from steamship.base import Task
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import DeleteRequest, Request
from steamship.base.response import Response
from steamship.data.search import Hit
from steamship.utils.metadata import metadata_to_str


class EmbedAndSearchRequest(Request):
    query: str
    docs: List[str]
    plugin_instance: str
    k: int = 1


class QueryResult(CamelModel):
    value: Optional[Hit] = None
    score: Optional[float] = None
    index: Optional[int] = None
    id: Optional[str] = None


class QueryResults(Request):
    items: List[QueryResult] = None


class EmbeddedItem(CamelModel):
    id: str = None
    index_id: str = None
    file_id: str = None
    block_id: str = None
    tag_id: str = None
    value: str = None
    external_id: str = None
    external_type: str = None
    metadata: Any = None
    embedding: List[float] = None

    def clone_for_insert(self) -> EmbeddedItem:
        """Produces a clone with a string representation of the metadata"""
        ret = EmbeddedItem(
            id=self.id,
            index_id=self.index_id,
            file_id=self.file_id,
            block_id=self.block_id,
            tag_id=self.tag_id,
            value=self.value,
            external_id=self.external_id,
            external_type=self.external_type,
            metadata=self.metadata,
            embedding=self.embedding,
        )
        if isinstance(ret.metadata, dict) or isinstance(ret.metadata, list):
            ret.metadata = json.dumps(ret.metadata)
        return ret


class IndexCreateRequest(Request):
    handle: str = None
    name: str = None
    plugin_instance: str = None
    fetch_if_exists: bool = True
    external_id: str = None
    external_type: str = None
    metadata: Any = None


class IndexInsertRequest(Request):
    index_id: str
    items: List[EmbeddedItem] = None
    value: str = None
    file_id: str = None
    block_type: str = None
    external_id: str = None
    external_type: str = None
    metadata: Any = None
    reindex: bool = True


class IndexItemId(CamelModel):
    index_id: str = None
    id: str = None


class IndexInsertResponse(Response):
    item_ids: List[IndexItemId] = None


class IndexEmbedRequest(Request):
    id: str


class IndexEmbedResponse(Response):
    id: Optional[str] = None


class IndexSearchRequest(Request):
    id: str
    query: str = None
    queries: List[str] = None
    k: int = 1
    include_metadata: bool = False


class IndexSnapshotRequest(Request):
    index_id: str
    window_size: int = None  # Used for unit testing


class IndexSnapshotResponse(Response):
    id: Optional[str] = None
    snapshot_id: str


class ListSnapshotsRequest(Request):
    id: str = None


class ListSnapshotsResponse(Response):
    snapshots: List[IndexSnapshotResponse]


class ListItemsRequest(Request):
    id: str = None
    file_id: str = None
    block_id: str = None
    span_id: str = None


class ListItemsResponse(Response):
    items: List[EmbeddedItem]


class DeleteSnapshotsRequest(Request):
    snapshot_id: str = None


class DeleteSnapshotsResponse(Response):
    snapshot_id: str = None


class EmbeddingIndex(CamelModel):
    """A persistent, read-optimized index over embeddings."""

    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None
    name: str = None
    plugin: str = None
    external_id: str = None
    external_type: str = None
    metadata: str = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        if "embeddingIndex" in obj:
            obj = obj["embeddingIndex"]
        elif "index" in obj:
            obj = obj["index"]
        return super().parse_obj(obj)

    def insert_file(
        self,
        file_id: str,
        block_type: str = None,
        external_id: str = None,
        external_type: str = None,
        metadata: Union[int, float, bool, str, List, Dict] = None,
        reindex: bool = True,
    ) -> IndexInsertResponse:
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = IndexInsertRequest(
            index_id=self.id,
            file_id=file_id,
            blockType=block_type,
            external_id=external_id,
            external_type=external_type,
            metadata=metadata,
            reindex=reindex,
        )
        return self.client.post(
            "embedding-index/item/create",
            req,
            expect=IndexInsertResponse,
        )

    def insert_many(
        self,
        items: List[Union[EmbeddedItem, str]],
        reindex: bool = True,
    ) -> IndexInsertResponse:
        new_items = []
        for item in items:
            if isinstance(item, str):
                new_items.append(EmbeddedItem(value=item))
            else:
                new_items.append(item)

        req = IndexInsertRequest(
            index_id=self.id,
            items=[item.clone_for_insert() for item in new_items],
            reindex=reindex,
        )
        return self.client.post(
            "embedding-index/item/create",
            req,
            expect=IndexInsertResponse,
        )

    def insert(
        self,
        value: str,
        external_id: str = None,
        external_type: str = None,
        metadata: Union[int, float, bool, str, List, Dict] = None,
        reindex: bool = True,
    ) -> IndexInsertResponse:

        req = IndexInsertRequest(
            index_id=self.id,
            value=value,
            external_id=external_id,
            external_type=external_type,
            metadata=metadata_to_str(metadata),
            reindex=reindex,
        )
        return self.client.post(
            "embedding-index/item/create",
            req,
            expect=IndexInsertResponse,
        )

    def embed(
        self,
    ) -> Task[IndexEmbedResponse]:
        req = IndexEmbedRequest(id=self.id)
        return self.client.post(
            "embedding-index/embed",
            req,
            expect=IndexEmbedResponse,
        )

    def create_snapshot(self) -> IndexSnapshotResponse:
        req = IndexSnapshotRequest(index_id=self.id)
        return self.client.post(
            "embedding-index/snapshot/create",
            req,
            expect=IndexSnapshotResponse,
        )

    def list_snapshots(self) -> ListSnapshotsResponse:
        req = ListSnapshotsRequest(id=self.id)
        return self.client.post(
            "embedding-index/snapshot/list",
            req,
            expect=ListSnapshotsResponse,
        )

    def list_items(
        self,
        file_id: str = None,
        block_id: str = None,
        span_id: str = None,
    ) -> ListItemsResponse:
        req = ListItemsRequest(id=self.id, file_id=file_id, block_id=block_id, spanId=span_id)
        return self.client.post(
            "embedding-index/item/list",
            req,
            expect=ListItemsResponse,
        )

    def delete_snapshot(
        self,
        snapshot_id: str,
    ) -> DeleteSnapshotsResponse:
        req = DeleteSnapshotsRequest(snapshotId=snapshot_id)
        return self.client.post(
            "embedding-index/snapshot/delete",
            req,
            expect=DeleteSnapshotsResponse,
        )

    def delete(self) -> EmbeddingIndex:
        return self.client.post(
            "embedding-index/delete",
            DeleteRequest(id=self.id),
            expect=EmbeddingIndex,
        )

    def search(
        self,
        query: Union[str, List[str]],
        k: int = 1,
        include_metadata: bool = False,
    ) -> Task[QueryResults]:
        if isinstance(query, list):
            req = IndexSearchRequest(
                id=self.id, queries=query, k=k, include_metadata=include_metadata
            )
        else:
            req = IndexSearchRequest(
                id=self.id, query=query, k=k, include_metadata=include_metadata
            )
        ret = self.client.post(
            "embedding-index/search",
            req,
            expect=QueryResults,
        )

        return ret

    @staticmethod
    def create(
        client: Client,
        handle: str = None,
        name: str = None,
        embedder_plugin_instance_handle: str = None,
        fetch_if_exists: bool = True,
        external_id: str = None,
        external_type: str = None,
        metadata: Any = None,
    ) -> EmbeddingIndex:
        req = IndexCreateRequest(
            handle=handle,
            name=name,
            plugin_instance=embedder_plugin_instance_handle,
            fetch_if_exists=fetch_if_exists,
            external_id=external_id,
            external_type=external_type,
            metadata=metadata,
        )
        return client.post(
            "embedding-index/create",
            req,
            expect=EmbeddingIndex,
        )
