"""Indexes a file."""
import uuid
from typing import List, Optional, cast

from pydantic import Field

from steamship.base.model import CamelModel
from steamship.base.tasks import Task
from steamship.client.steamship import Steamship
from steamship.data import TagKind, TagValueKey
from steamship.data.block import Block
from steamship.data.embeddings import IndexInsertResponse
from steamship.data.file import File
from steamship.data.plugin.index_plugin_instance import EmbeddingIndexPluginInstance, SearchResults
from steamship.data.tags.tag import Tag
from steamship.data.tags.tag_constants import DocTag

EMBEDDING_PLUGIN = "openai-embedder"
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIMENSIONS = 1536


class ChunkingVectorStore(CamelModel):
    client: Steamship
    index: EmbeddingIndexPluginInstance
    index_name: str = Field(None, "Name of the embedding index. Lowercase letters and dashes only.")
    default_context_window_size: int = Field(
        200, "Approximate size, in characters, of the context window"
    )
    default_context_window_overlap: int = Field(
        50, "Approximate size, in characters, of the desired context window overlap"
    )

    def __init__(
        self,
        client: Steamship,
        index_name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(client=client, index_name=index_name or uuid.uuid4().hex, **kwargs)
        self.index: EmbeddingIndexPluginInstance = cast(
            EmbeddingIndexPluginInstance,
            self.client.use_plugin(
                plugin_handle="embedding-index",
                instance_handle=self.index_name,
                config={
                    "embedder": {
                        "plugin_handle": EMBEDDING_PLUGIN,
                        "instance_handle": self.index_name,
                        "fetch_if_exists": True,
                        "config": {
                            "model": EMBEDDING_MODEL,
                            "dimensionality": EMBEDDING_DIMENSIONS,
                        },
                    }
                },
                fetch_if_exists=True,
            ),
        )
        self.index.embedder.wait_for_init()

    def _metadata_for_file(self, file: File) -> dict:
        """Generate standard helpful metadata for a File."""
        metadata = {"file_id": file.id}

        for tag in file.tags:
            if tag.kind == TagKind.DOCUMENT:
                if tag.name in [DocTag.SOURCE, DocTag.TITLE, DocTag.STATUS]:
                    metadata[tag.name] = tag.value.get(TagValueKey.STRING_VALUE)

        return metadata

    def _metadata_for_block(self, block: Block) -> dict:
        """Generate standard helpful metadata for a Block."""
        if not block.tags:
            return {}

        metadata = {"block_id": block.id}
        for tag in block.tags:
            if tag.name == DocTag.PAGE:
                page_num = tag.value.get(TagValueKey.NUMBER_VALUE)
                if page_num is not None:
                    metadata["page"] = page_num

        return metadata

    def insert_tags(
        self, tags: List[Tag], allow_long_records: Optional[bool] = None
    ) -> IndexInsertResponse:
        """Insert a list of Tag objects."""
        return self.index.insert(tags, allow_long_records=allow_long_records)

    def insert_file(
        self,
        file: File,
        context_window_size: Optional[int] = None,
        context_window_overlap: Optional[int] = None,
        allow_long_records: Optional[bool] = None,
    ) -> IndexInsertResponse:
        """Insert an entire file by chunking the text of each block according a sliding context window."""

        context_window_size = context_window_size or self.default_context_window_size
        context_window_overlap = context_window_overlap or self.default_context_window_overlap

        file_metadata = self._metadata_for_file(file)

        to_index = []

        for block in file.blocks:
            # Load the page_id from the block if it exists
            block_metadata = self._metadata_for_block(block)

            # Consolidate, giving the block metadata preference
            metadata = {}
            metadata.update(file_metadata)
            metadata.update(block_metadata)

            for i in range(0, len(block.text), self.config.context_window_size):
                # Calculate the extent of the window plus the overlap at the edges
                min_range = max(0, i - context_window_overlap)
                max_range = min(len(block.text), i + context_window_size + context_window_overlap)

                # Get the text covering that chunk.
                text = block.text[min_range:max_range]

                # Create a Tag for index insertion.
                # Terminology Note: Steamship indexes at the level of 'Tag' instead of 'Document' (a la LangChain)
                to_index.append(Tag(text=text, value=metadata))

        # Add the tags
        return self.insert_tags(to_index, allow_long_records=allow_long_records)

    def search(self, query: str, k: Optional[int] = None) -> Task[SearchResults]:
        """Search the embedding index.

        This wrapper implementation simply projects the `Hit` data structure into a `Tag`
        """
        return self.index.search(query=query, k=k)
