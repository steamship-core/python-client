import json
from dataclasses import dataclass
from typing import List, Dict, Union, TypeVar, Generic

from steamship.base import Client, Request, Response, metadata_to_str
from steamship.data.search import Hit


@dataclass
class EmbedAndSearchRequest(Request):
    query: str
    docs: List[str]
    pluginInstance: str
    k: int = 1


#TODO: These types are not generics like the Swift QueryResult/QueryResults.
@dataclass
class QueryResult():
    value: Hit
    score: float
    index: int
    id: str

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "QueryResult":
        value = Hit.from_dict(d.get("value", {}))
        return QueryResult(
            value = value,
            score = d.get('score'),
            index = d.get('index'),
            id = d.get('id')
        )

@dataclass
class QueryResults(Request):
    items: List[QueryResult] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "QueryResults":
        items = [QueryResult.from_dict(h) for h in (d.get("items", []) or [])]
        return QueryResults(
            items=items
        )





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
            embedding=self.embedding
        )
        if isinstance(ret.metadata, dict) or isinstance(ret.metadata, list):
            ret.metadata = json.dumps(ret.metadata)
        return ret

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbeddedItem":
        return EmbeddedItem(
            id=d.get('id', None),
            indexId=d.get('indexId', None),
            fileId=d.get('fileId', None),
            blockId=d.get('blockId', None),
            tagId=d.get('tagId', None),
            value=d.get('value', None),
            externalId=d.get('externalId', None),
            externalType=d.get('externalType', None),
            metadata=d.get('metadata', None),
            embedding=d.get('embedding', None),
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
        return IndexItemId(
            indexId=d.get('indexId', None),
            id=d.get('id', None)
        )


@dataclass
class IndexInsertResponse:
    itemIds: List[IndexItemId] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "IndexInsertResponse":
        return IndexInsertResponse(
            itemIds=[IndexItemId.from_dict(x) for x in (d.get('itemIds', []) or [])]
        )


@dataclass
class IndexEmbedRequest(Request):
    id: str


@dataclass
class IndexEmbedResponse:
    id: str

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "IndexEmbedResponse":
        return IndexEmbedResponse(
            id=d.get('id', None)
        )


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
            id=d.get('id', None),
            snapshotId=d.get('snapshotId', None)
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
            snapshots=[IndexSnapshotResponse.from_dict(dd) for dd in (d.get('snapshots', []) or [])]
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
            items=[EmbeddedItem.from_dict(dd) for dd in (d.get('items', []) or [])]
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
    """A persistent, read-optimized index over embeddings.
    """

    client: Client = None
    id: str = None
    handle: str = None
    name: str = None
    plugin: str = None
    externalId: str = None
    externalType: str = None
    metadata: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "EmbeddingIndex":
        if 'embeddingIndex' in d:
            d = d['embeddingIndex']
        elif 'index' in d:
            d = d['index']
        return EmbeddingIndex(
            client=client,
            id=d.get('id', None),
            handle=d.get('handle', None),
            name=d.get('name', None),
            plugin=d.get('plugin', None),
            externalId=d.get('externalId', None),
            externalType=d.get('externalType', None),
            metadata=d.get('metadata', None)
        )

    def insert_file(
            self,
            fileId: str,
            blockType: str = None,
            externalId: str = None,
            externalType: str = None,
            metadata: Union[int, float, bool, str, List, Dict] = None,
            reindex: bool = True,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> Response[IndexInsertResponse]:
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = IndexInsertRequest(
            indexId=self.id,
            fileId=fileId,
            blockType=blockType,
            externalId=externalId,
            externalType=externalType,
            metadata=metadata,
            reindex=reindex,
        )
        return self.client.post(
            'embedding-index/item/create',
            req,
            expect=IndexInsertResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def insert_many(
            self,
            items: List[Union[EmbeddedItem, str]],
            reindex: bool = True,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> Response[IndexInsertResponse]:
        newItems = []
        for item in items:
            if type(item) == str:
                newItems.append(EmbeddedItem(value=item))
            else:
                newItems.append(item)

        req = IndexInsertRequest(
            indexId=self.id,
            value=None,
            items=[item.clone_for_insert() for item in newItems],
            reindex=reindex,
        )
        return self.client.post(
            'embedding-index/item/create',
            req,
            expect=IndexInsertResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def insert(
            self,
            value: str,
            externalId: str = None,
            externalType: str = None,
            metadata: Union[int, float, bool, str, List, Dict] = None,
            reindex: bool = True,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> Response[IndexInsertResponse]:

        req = IndexInsertRequest(
            indexId=self.id,
            value=value,
            items=None,
            externalId=externalId,
            externalType=externalType,
            metadata=metadata_to_str(metadata),
            reindex=reindex,
        )
        return self.client.post(
            'embedding-index/item/create',
            req,
            expect=IndexInsertResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def embed(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> Response[IndexEmbedResponse]:
        req = IndexEmbedRequest(
            self.id
        )
        return self.client.post(
            'embedding-index/embed',
            req,
            expect=IndexEmbedResponse,
            asynchronous=True,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def create_snapshot(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> Response[IndexSnapshotResponse]:
        req = IndexSnapshotRequest(
            indexId=self.id
        )
        return self.client.post(
            'embedding-index/snapshot/create',
            req,
            expect=IndexSnapshotResponse,
            asynchronous=True,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def list_snapshots(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> Response[ListSnapshotsResponse]:
        req = ListSnapshotsRequest(
            id=self.id
        )
        return self.client.post(
            'embedding-index/snapshot/list',
            req,
            expect=ListSnapshotsResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def list_items(
            self,
            fileId: str = None,
            blockId: str = None,
            spanId: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> Response[ListItemsResponse]:
        req = ListItemsRequest(
            id=self.id,
            fileId=fileId,
            blockId=blockId,
            spanId=spanId
        )
        return self.client.post(
            'embedding-index/item/list',
            req,
            expect=ListItemsResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def delete_snapshot(
            self,
            snapshot_id: str,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> Response[DeleteSnapshotsResponse]:
        req = DeleteSnapshotsRequest(
            snapshotId=snapshot_id
        )
        return self.client.post(
            'embedding-index/snapshot/delete',
            req,
            expect=DeleteSnapshotsResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def delete(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> "Response[EmbeddingIndex]":
        return self.client.post(
            'embedding-index/delete',
            DeleteEmbeddingIndexRequest(id=self.id),
            expect=EmbeddingIndex,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def search(
            self,
            query: Union[str, List[str]],
            k: int = 1,
            includeMetadata: bool = False,
            pd=False,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> Response[QueryResults]:
        if type(query) == list:
            req = IndexSearchRequest(
                self.id,
                query=None,
                queries=query,
                k=k,
                includeMetadata=includeMetadata,
            )
        else:
            req = IndexSearchRequest(
                self.id,
                query=query,
                queries=None,
                k=k,
                includeMetadata=includeMetadata,
            )
        ret = self.client.post(
            'embedding-index/search',
            req,
            expect=QueryResults,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

        if pd is False:
            return ret

        import pandas as pd  # type: ignore
        return pd.DataFrame([(hit.score, hit.value) for hit in ret.data.hits], columns=['Score', 'Value'])

    @staticmethod
    def create(
            client: Client,
            handle: str = None,
            name: str = None,
            pluginInstance: str = None,
            upsert: bool = True,
            externalId: str = None,
            externalType: str = None,
            metadata: any = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> "Response[EmbeddingIndex]":
        req = IndexCreateRequest(
            handle=handle,
            name=name,
            pluginInstance=pluginInstance,
            upsert=upsert,
            externalId=externalId,
            externalType=externalType,
            metadata=metadata,
        )
        return client.post(
            'embedding-index/create',
            req,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space,
            expect=EmbeddingIndex
        )
