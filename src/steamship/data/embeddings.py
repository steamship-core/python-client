from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from steamship.base import Client, Request, Response, metadata_to_str
from steamship.data.search import Hit


class EmbedAndSearchRequest(Request):
    query: str
    docs: List[str]
    pluginInstance: str
    k: int = 1


# TODO: These types are not generics like the Swift QueryResult/QueryResults.
class QueryResult(BaseModel):
    value: Optional[Hit] = None
    score: Optional[float] = None
    index: Optional[int] = None
    id: Optional[str] = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> QueryResult:
        value = Hit.from_dict(d.get("value", {}))
        return QueryResult(value=value, score=d.get("score"), index=d.get("index"), id=d.get("id"))


class QueryResults(Request):
    items: List[QueryResult] = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> QueryResults:
        # TODO: Try to always use client through inheritance
        items = [QueryResult.from_dict(h) for h in (d.get("items", []) or [])]
        return QueryResults(items=items)


class EmbeddedItem(BaseModel):
    id: str = None
    indexId: str = None
    fileId: str = None
    blockId: str = None
    tagId: str = None
    value: str = None
    externalId: str = None
    externalType: str = None
    metadata: Any = None
    embedding: List[float] = None

    def clone_for_insert(self) -> EmbeddedItem:
        """Produces a clone with a string representation of the metadata"""
        ret = EmbeddedItem(
            id=self.id,
            indexId=self.indexId,
            fileId=self.fileId,
            blockId=self.blockId,
            tagId=self.tagId,
            value=self.value,
            externalId=self.externalId,
            externalType=self.externalType,
            metadata=self.metadata,
            embedding=self.embedding,
        )
        if isinstance(ret.metadata, dict) or isinstance(ret.metadata, list):
            ret.metadata = json.dumps(ret.metadata)
        return ret

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> EmbeddedItem:
        return EmbeddedItem(
            id=d.get("id"),
            indexId=d.get("indexId"),
            fileId=d.get("fileId"),
            blockId=d.get("blockId"),
            tagId=d.get("tagId"),
            value=d.get("value"),
            externalId=d.get("externalId"),
            externalType=d.get("externalType"),
            metadata=d.get("metadata"),
            embedding=d.get("embedding"),
        )


class IndexCreateRequest(Request):
    handle: str = None
    name: str = None
    pluginInstance: str = None
    upsert: bool = True
    externalId: str = None
    externalType: str = None
    metadata: Any = None


class IndexInsertRequest(Request):
    indexId: str
    items: List[EmbeddedItem] = None
    value: str = None
    fileId: str = None
    blockType: str = None
    externalId: str = None
    externalType: str = None
    metadata: Any = None
    reindex: bool = True


class IndexItemId(BaseModel):
    indexId: str = None
    id: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> IndexItemId:
        return IndexItemId(indexId=d.get("indexId"), id=d.get("id"))


class IndexInsertResponse(BaseModel):
    itemIds: List[IndexItemId] = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> IndexInsertResponse:
        return IndexInsertResponse(
            itemIds=[IndexItemId.from_dict(x) for x in (d.get("itemIds", []) or [])]
        )


class IndexEmbedRequest(Request):
    id: str


class IndexEmbedResponse(BaseModel):
    id: Optional[str] = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> IndexEmbedResponse:
        return IndexEmbedResponse(id=d.get("id"))


class IndexSearchRequest(Request):
    id: str
    query: str = None
    queries: List[str] = None
    k: int = 1
    includeMetadata: bool = False


class IndexSnapshotRequest(Request):
    indexId: str
    # This variable is intended only to support
    # unit testing.
    windowSize: int = None


class IndexSnapshotResponse(BaseModel):
    id: Optional[str] = None
    snapshotId: str

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> IndexSnapshotResponse:
        return IndexSnapshotResponse(id=d.get("id"), snapshotId=d.get("snapshotId"))


class ListSnapshotsRequest(Request):
    id: str = None


class ListSnapshotsResponse(BaseModel):
    snapshots: List[IndexSnapshotResponse]

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> ListSnapshotsResponse:
        return ListSnapshotsResponse(
            snapshots=[IndexSnapshotResponse.from_dict(dd) for dd in (d.get("snapshots", []) or [])]
        )


class ListItemsRequest(Request):
    id: str = None
    fileId: str = None
    blockId: str = None
    spanId: str = None


class ListItemsResponse(BaseModel):
    items: List[EmbeddedItem]

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> ListItemsResponse:
        return ListItemsResponse(
            items=[EmbeddedItem.from_dict(dd) for dd in (d.get("items", []) or [])]
        )


class DeleteSnapshotsRequest(Request):
    snapshotId: str = None


class DeleteSnapshotsResponse(Request):
    snapshotId: str = None


class DeleteEmbeddingIndexRequest(Request):
    id: str


class EmbeddingIndex(BaseModel):
    """A persistent, read-optimized index over embeddings."""

    client: Client = None
    id: str = None
    handle: str = None
    name: str = None
    plugin: str = None
    external_id: str = None
    external_type: str = None
    metadata: str = None

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> EmbeddingIndex:
        if "embeddingIndex" in d:
            d = d["embeddingIndex"]
        elif "index" in d:
            d = d["index"]
        return EmbeddingIndex(
            client=client,
            id=d.get("id"),
            handle=d.get("handle"),
            name=d.get("name"),
            plugin=d.get("plugin"),
            external_id=d.get("externalId"),
            external_type=d.get("externalType"),
            metadata=d.get("metadata"),
        )

    def insert_file(
        self,
        file_id: str,
        block_type: str = None,
        external_id: str = None,
        external_type: str = None,
        metadata: Union[int, float, bool, str, List, Dict] = None,
        reindex: bool = True,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[IndexInsertResponse]:
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = IndexInsertRequest(
            indexId=self.id,
            fileId=file_id,
            blockType=block_type,
            externalId=external_id,
            externalType=external_type,
            metadata=metadata,
            reindex=reindex,
        )
        return self.client.post(
            "embedding-index/item/create",
            req,
            expect=IndexInsertResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def insert_many(
        self,
        items: List[Union[EmbeddedItem, str]],
        reindex: bool = True,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[IndexInsertResponse]:
        new_items = []
        for item in items:
            if type(item) == str:
                new_items.append(EmbeddedItem(value=item))
            else:
                new_items.append(item)

        req = IndexInsertRequest(
            indexId=self.id,
            items=[item.clone_for_insert() for item in new_items],
            reindex=reindex,
        )
        return self.client.post(
            "embedding-index/item/create",
            req,
            expect=IndexInsertResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def insert(
        self,
        value: str,
        external_id: str = None,
        external_type: str = None,
        metadata: Union[int, float, bool, str, List, Dict] = None,
        reindex: bool = True,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[IndexInsertResponse]:

        req = IndexInsertRequest(
            indexId=self.id,
            value=value,
            externalId=external_id,
            externalType=external_type,
            metadata=metadata_to_str(metadata),
            reindex=reindex,
        )
        return self.client.post(
            "embedding-index/item/create",
            req,
            expect=IndexInsertResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def embed(
        self, space_id: str = None, space_handle: str = None, space: Any = None
    ) -> Response[IndexEmbedResponse]:
        req = IndexEmbedRequest(id=self.id)
        return self.client.post(
            "embedding-index/embed",
            req,
            expect=IndexEmbedResponse,
            asynchronous=True,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def create_snapshot(
        self, space_id: str = None, space_handle: str = None, space: Any = None
    ) -> Response[IndexSnapshotResponse]:
        req = IndexSnapshotRequest(indexId=self.id)
        return self.client.post(
            "embedding-index/snapshot/create",
            req,
            expect=IndexSnapshotResponse,
            asynchronous=True,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    # TODO (enias): Can these be generic list operations for all file types?
    def list_snapshots(
        self, space_id: str = None, space_handle: str = None, space: Any = None
    ) -> Response[ListSnapshotsResponse]:
        req = ListSnapshotsRequest(id=self.id)
        return self.client.post(
            "embedding-index/snapshot/list",
            req,
            expect=ListSnapshotsResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def list_items(
        self,
        file_id: str = None,
        block_id: str = None,
        span_id: str = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[ListItemsResponse]:
        req = ListItemsRequest(id=self.id, fileId=file_id, blockId=block_id, spanId=span_id)
        return self.client.post(
            "embedding-index/item/list",
            req,
            expect=ListItemsResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def delete_snapshot(
        self,
        snapshot_id: str,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[DeleteSnapshotsResponse]:
        req = DeleteSnapshotsRequest(snapshotId=snapshot_id)
        return self.client.post(
            "embedding-index/snapshot/delete",
            req,
            expect=DeleteSnapshotsResponse,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def delete(
        self, space_id: str = None, space_handle: str = None, space: Any = None
    ) -> Response[EmbeddingIndex]:
        return self.client.post(
            "embedding-index/delete",
            DeleteEmbeddingIndexRequest(id=self.id),
            expect=EmbeddingIndex,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def search(
        self,
        query: Union[str, List[str]],
        k: int = 1,
        include_metadata: bool = False,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[QueryResults]:
        if type(query) == list:
            req = IndexSearchRequest(
                id=self.id, queries=query, k=k, includeMetadata=include_metadata
            )
        else:
            req = IndexSearchRequest(id=self.id, query=query, k=k, includeMetadata=include_metadata)
        ret = self.client.post(
            "embedding-index/search",
            req,
            expect=QueryResults,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

        return ret

    @staticmethod
    def create(
        client: Client,
        handle: str = None,
        name: str = None,
        plugin_instance: str = None,
        upsert: bool = True,
        external_id: str = None,
        external_type: str = None,
        metadata: Any = None,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
    ) -> Response[EmbeddingIndex]:
        req = IndexCreateRequest(
            handle=handle,
            name=name,
            pluginInstance=plugin_instance,
            upsert=upsert,
            externalId=external_id,
            externalType=external_type,
            metadata=metadata,
        )
        return client.post(
            "embedding-index/create",
            req,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
            expect=EmbeddingIndex,
        )
