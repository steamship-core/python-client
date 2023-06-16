"""Answers questions with the assistance of a VectorSearch plugin."""
from abc import ABC
from typing import Optional, cast

from steamship import Steamship
from steamship.agents.schema import Tool
from steamship.data.plugin.index_plugin_instance import EmbeddingIndexPluginInstance


class VectorSearchTool(Tool, ABC):
    """Abstract Base Class that provides helper data for a tool that uses Vector Search."""

    embedding_index_handle: Optional[str] = "embedding-index"
    embedding_index_version: Optional[str] = None
    embedding_index_config: Optional[dict] = {
        "embedder": {
            "plugin_handle": "openai-embedder",
            "plugin_instance_handle": "text-embedding-ada-002",
            "fetch_if_exists": True,
            "config": {"model": "text-embedding-ada-002", "dimensionality": 1536},
        }
    }
    embedding_index_instance_handle: str = "default-embedding-index"

    def get_embedding_index(self, client: Steamship) -> EmbeddingIndexPluginInstance:
        index = client.use_plugin(
            plugin_handle=self.embedding_index_handle,
            instance_handle=self.embedding_index_instance_handle,
            config=self.embedding_index_config,
            fetch_if_exists=True,
        )
        return cast(EmbeddingIndexPluginInstance, index)
