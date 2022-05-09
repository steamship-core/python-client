import json
from dataclasses import dataclass
from typing import List, Dict, Union

from steamship.base import Client, Request, Response, metadata_to_str
from steamship.data.search import Hit


@dataclass
class EmbedAndSearchRequest(Request):
    query: str
    docs: List[str]
    pluginInstance: str
    k: int = 1


# TODO: These types are not generics like the Swift QueryResult/QueryResults.
@dataclass
class QueryResult:
    value: Hit
    score: float
    index: int
    id: str

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "QueryResult":
        value = Hit.from_dict(d.get("value", {}))
        return QueryResult(
            value=value, score=d.get("score"), index=d.get("index"), id=d.get("id")
        )


@dataclass
class QueryResults(Request):
    items: List[QueryResult] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "QueryResults":
        items = [QueryResult.from_dict(h) for h in (d.get("items", []) or [])]
        return QueryResults(items=items)


@dataclass
class EmbeddedItem:
    id: str = None
    indexId: str = None
    fileId: str = None
    blockId: str = None
    tagId: str = None
    value: str = None
    externalId: str = None
    externalType: str = None
    metadata: any = None
    embedding: List[float] = None

    def clone_for_insert(self) -> "EmbeddedItem":
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

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbeddedItem":
        return EmbeddedItem(
            id=d.get("id", None),
            indexId=d.get("indexId", None),
            fileId=d.get("fileId", None),
            blockId=d.get("blockId", None),
            tagId=d.get("tagId", None),
            value=d.get("value", None),
            externalId=d.get("externalId", None),
            externalType=d.get("externalType", None),
            metadata=d.get("metadata", None),
            embedding=d.get("embedding", None),
        )


@dataclass
class IndexCreateRequest(Request):
    handle: str = None
    name: str = None
    pluginInstance: str = None
    upsert: bool = True
    externalId: str = None
    externalType: str = None
    metadata: any = None


@dataclass
class IndexInsertRequest(Request):
    indexId: str
    items: List[EmbeddedItem] = None
    value: str = None
    fileId: str = None
    blockType: str = None
    externalId: str = None
    externalType: str = None
    metadata: any = None
    reindex: bool = True


@dataclass
class IndexItemId:
    indexId: str = None
    id: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "IndexItemId":
        return IndexItemId(indexId=d.get("indexId", None), id=d.get("id", None))


@dataclass
class IndexInsertResponse:
    itemIds: List[IndexItemId] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "IndexInsertResponse":
        return IndexInsertResponse(
            itemIds=[IndexItemId.from_dict(x) for x in (d.get("itemIds", []) or [])]
        )


@dataclass
class IndexEmbedRequest(Request):
    id: str


@dataclass
class IndexEmbedResponse:
    id: str

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "IndexEmbedResponse":
        return IndexEmbedResponse(id=d.get("id", None))


@dataclass
class IndexSearchRequest(Request):
    id: str
    query: str = None
    queries: List[str] = None
    k: int = 1
    includeMetadata: bool = False


@dataclass
class IndexSnapshotRequest(Request):
    indexId: str
    # This variable is intended only to support
    # unit testing.
    windowSize: int = None


@dataclass
class IndexSnapshotResponse:
    id: str
    snapshotId: str

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "IndexSnapshotResponse":
        return IndexSnapshotResponse(
            id=d.get("id", None), snapshotId=d.get("snapshotId", None)
        )


@dataclass
class ListSnapshotsRequest(Request):
    id: str = None


@dataclass
class ListSnapshotsResponse:
    snapshots: List[IndexSnapshotResponse]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "IndexSnapshotResponse":
        return IndexSnapshotResponse(
            snapshots=[
                IndexSnapshotResponse.from_dict(dd)
                for dd in (d.get("snapshots", []) or [])
            ]
        )


@dataclass
class ListItemsRequest(Request):
    id: str = None
    fileId: str = None
    blockId: str = None
    spanId: str = None


@dataclass
class ListItemsResponse:
    items: List[EmbeddedItem]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ListItemsResponse":
        return ListItemsResponse(
            items=[EmbeddedItem.from_dict(dd) for dd in (d.get("items", []) or [])]
        )


@dataclass
class DeleteSnapshotsRequest(Request):
    snapshotId: str = None


@dataclass
class DeleteSnapshotsResponse(Request):
    snapshotId: str = None


@dataclass
class DeleteEmbeddingIndexRequest(Request):
    id: str


@dataclass
class EmbeddingIndex:
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
    def from_dict(d: any, client: Client = None) -> "EmbeddingIndex":
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
        space: any = None,
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
        space: any = None,
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
        space: any = None,
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
        self, space_id: str = None, space_handle: str = None, space: any = None
    ) -> Response[IndexEmbedResponse]:
        req = IndexEmbedRequest(self.id)
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
        self, space_id: str = None, space_handle: str = None, space: any = None
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
        self, space_id: str = None, space_handle: str = None, space: any = None
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
        space: any = None,
    ) -> Response[ListItemsResponse]:
        req = ListItemsRequest(
            id=self.id, fileId=file_id, blockId=block_id, spanId=span_id
        )
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
        space: any = None,
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
        self, space_id: str = None, space_handle: str = None, space: any = None
    ) -> "Response[EmbeddingIndex]":
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
        pd=False,
        space_id: str = None,
        space_handle: str = None,
        space: any = None,
    ) -> Response[QueryResults]:
        if type(query) == list:
            req = IndexSearchRequest(
                self.id, queries=query, k=k, includeMetadata=include_metadata
            )
        else:
            req = IndexSearchRequest(
                self.id, query=query, k=k, includeMetadata=include_metadata
            )
        ret = self.client.post(
            "embedding-index/search",
            req,
            expect=QueryResults,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

        if pd is False:
            return ret

        # noinspection PyPackageRequirements
        import pandas as pd  # type: ignore

        return pd.DataFrame(
            [(hit.score, hit.value) for hit in ret.data.hits],
            columns=["Score", "Value"],
        )

    @staticmethod
    def create(
        client: Client,
        handle: str = None,
        name: str = None,
        plugin_instance: str = None,
        upsert: bool = True,
        external_id: str = None,
        external_type: str = None,
        metadata: any = None,
        space_id: str = None,
        space_handle: str = None,
        space: any = None,
    ) -> "Response[EmbeddingIndex]":
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
