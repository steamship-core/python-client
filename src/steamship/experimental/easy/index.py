"""Indexes a file."""
from typing import List, Optional

from pydantic import Field

from steamship import Block, DocTag, File, Tag
from steamship.base.model import CamelModel
from steamship.client.steamship import Steamship
from steamship.data import TagKind, TagValueKey
from steamship.data.embeddings import IndexInsertResponse
from steamship.data.plugin.index_plugin_instance import EmbeddingIndexPluginInstance


class ChunkingVectorStore(CamelModel):
    client: Steamship
    index: EmbeddingIndexPluginInstance

    default_context_window_size: int = Field(
        200, "Approximate size, in characters, of the context window"
    )
    default_context_window_overlap: int = Field(
        50, "Approximate size, in characters, of the desired context window overlap"
    )

    def _metadata_for_file(self, file: File) -> dict:
        metadata = {"file_id": file.id}

        for tag in file.tags:
            if tag.kind == TagKind.DOCUMENT:
                if tag.name in [DocTag.SOURCE, DocTag.TITLE, DocTag.STATUS]:
                    metadata[tag.name] = tag.value.get(TagValueKey.STRING_VALUE)

        return metadata

    def _metadata_for_block(self, block: Block) -> dict:
        if not block.tags:
            return {}

        metadata = {}
        for tag in block.tags:
            if tag.name == DocTag.PAGE:
                page_num = tag.value.get(TagValueKey.NUMBER_VALUE)
                if page_num is not None:
                    metadata["page"] = page_num

        return metadata

    def insert_tags(
        self, tags: List[Tag], allow_long_records: Optional[bool] = None
    ) -> IndexInsertResponse:
        return self.index.insert(tags, allow_long_records=allow_long_records)

    def insert_file(
        self,
        file: File,
        context_window_size: Optional[int] = None,
        context_window_overlap: Optional[int] = None,
        allow_long_records: Optional[bool] = None,
    ) -> IndexInsertResponse:
        """Inserts"""
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

    def query(self, search: str, k: int):
        pass
