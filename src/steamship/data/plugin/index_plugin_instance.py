from typing import Any, Dict, Optional

from pydantic import Field

from steamship import SteamshipError
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.data.embeddings import EmbeddingIndex
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


class EmbeddingIndexPluginInstance(PluginInstance):
    """A persistent, read-optimized index over embeddings.

    This is currently implemented as an object which behaves like a PluginInstance even though
    it isn't from an implementation perspective on the back-end.
    """

    client: Client = Field(None, exclude=True)
    embedder: PluginInstance = Field(None, exclude=True)
    index: EmbeddingIndex = Field(None, exclude=True)

    def delete(self):
        return self.index.delete()

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
        embedder_invocation = EmbedderInvocation.parse_obj(config.get("embedder"))

        # Create the embedder
        embedder = client.use_plugin(**embedder_invocation.dict())

        # Create the index
        index = EmbeddingIndex.create(
            client=client,
            handle=handle,
            plugin_instance=embedder.handle,
            fetch_if_exists=fetch_if_exists,
        )

        # Now return the plugin wrapper
        return EmbeddingIndexPluginInstance(
            id=index.id, handle=index.handle, index=index, embedder=embedder
        )
