from typing import Any, Dict, List, Optional, cast

from pydantic import Field

from steamship import SteamshipError, Tag, Task
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.data.embeddings import EmbeddedItem, EmbeddingIndex, QueryResult, QueryResults
from steamship.data.plugin.plugin_instance import PluginInstance


class EmbedderInvocation(CamelModel):
    """The parameters capable of creating/fetching an Embedder (Tagger) Plugin Instance."""

    plugin_handle: str
    instance_handle: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    fetch_if_exists: bool = True


# Hard coded list of plugin handles that the Steamship client will use to create
# instance of this object instead of a normal PluginInstance.
SHIMMED_INDEX_PLUGIN_HANDLES = ["embedding-index"]


class SearchResult(CamelModel):
    """A single scored search result -- which is always a tag.

    This class is intended to eventually replace the QueryResult object currently used with the Embedding layer."""

    tag: Optional[Tag] = None
    score: Optional[float] = None

    @staticmethod
    def from_query_result(query_result: QueryResult):
        hit = query_result.value
        tag = Tag(
            id=hit.id,
            kind=hit.external_type,
            name=hit.external_id,
            value=hit.metadata,
        )
        return SearchResult(tag=tag, score=query_result.score)


class SearchResults(CamelModel):
    """Results of a search operation -- which is always a list of ranked tag.

    This class is intended to eventually replace the QueryResults object currently used with the Embedding layer.
    TODO: add in paging support."""

    items: List[QueryResult] = None

    @staticmethod
    def from_query_results(query_results: QueryResults):
        items = [SearchResult.from_query_result(qr) for qr in query_results.items or []]
        return SearchResults(items=items)


class EmbeddingIndexPluginInstance(PluginInstance):
    """A persistent, read-optimized index over embeddings.

    This is currently implemented as an object which behaves like a PluginInstance even though
    it isn't from an implementation perspective on the back-end.
    """

    client: Client = Field(None, exclude=True)
    embedder: PluginInstance = Field(None, exclude=True)
    index: EmbeddingIndex = Field(None, exclude=True)

    def delete(self):
        """Delete the EmbeddingIndexPluginInstnace.

        For now, we will have this correspond to deleting the `index` but not the `embedder`. This is likely
        a temporary design.
        """
        return self.index.delete()

    def insert(self, tags: List[Tag]):
        """Insert tags into the embedding index."""
        for tag in tags:
            if not tag.text:
                raise SteamshipError(
                    message="Please set the `text` field of your Tag before inserting it into an index."
                )

        # Now we need to prepare an EmbeddingIndexItem of a particular shape that encodes the tag.
        embedded_items = [
            EmbeddedItem(
                file_id=tag.file_id,
                block_id=tag.block_id,
                tag_id=tag.id,
                value=tag.text,
                external_id=tag.name,
                external_type=tag.kind,
                metadata=tag.value,
            )
            for tag in tags
        ]

        # We always reindex in this new style; to not do so is to expose details (when embedding occurrs) we'd rather
        # not have users exercise control over.
        self.index.insert_many(embedded_items, reindex=True)

        # We always snapshot in this new style; to not do so is to expose details we'd rather not have
        # users exercise control over.
        self.index.create_snapshot()

    def search(self, query: str, k: Optional[int] = None) -> Task[SearchResults]:
        """Search the embedding index.

        This wrapper implementation simply projects the `Hit` data structure into a `Tag`
        """
        # Metadata will always be included; this is the equivalent of Tag.value
        wrapped_result = self.index.search(query, k=k, include_metadata=True)

        # For now, we'll have to do this synchronously since we're trying to avoid changing things on the engine.
        wrapped_result.wait()

        # We're going to do a switcheroo on the output type of Task here.
        search_results = SearchResults.from_query_results(wrapped_result.output)
        wrapped_result.output = search_results

        # Return the index's search result, but projected into the data structure of Tags
        return cast(Task[SearchResults], wrapped_result)

    @staticmethod
    def create(
        client: Any,
        plugin_id: str = None,
        plugin_handle: str = None,
        plugin_version_id: str = None,
        plugin_version_handle: str = None,
        handle: str = None,
        fetch_if_exists: bool = True,
        config: Dict[str, Any] = None,
    ) -> "EmbeddingIndexPluginInstance":
        """Create a class that simulates an embedding index re-implemented as a PluginInstance."""
        if plugin_handle not in SHIMMED_INDEX_PLUGIN_HANDLES:
            raise SteamshipError(message=f"No Embedding Index of type {plugin_handle} was found.")

        # Perform a manual config validation check since the configuration isn't actually being sent up to the Engine.
        # In this case, an embedding index has special behavior which is to instantiate/fetch an Embedder that it can use.
        if "embedder" not in config:
            raise SteamshipError(
                message="Config key missing. Please include a field named `embedder` with type `EmbedderInvocation`."
            )

        # Just for pydantic validation.
        embedder_invocation = EmbedderInvocation.parse_obj(config["embedder"])

        # Create the embedder
        embedder = client.use_plugin(**embedder_invocation.dict())

        # Create the index
        index = EmbeddingIndex.create(
            client=client,
            handle=handle,
            embedder_plugin_instance_handle=embedder.handle,
            fetch_if_exists=fetch_if_exists,
        )

        # Now return the plugin wrapper
        return EmbeddingIndexPluginInstance(
            id=index.id, handle=index.handle, index=index, embedder=embedder
        )
