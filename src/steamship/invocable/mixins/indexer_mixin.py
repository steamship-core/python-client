from typing import Optional, cast

from steamship import Block, DocTag, File, Steamship, Tag
from steamship.data import TagKind, TagValueKey
from steamship.data.plugin.index_plugin_instance import EmbeddingIndexPluginInstance, SearchResults
from steamship.invocable import post
from steamship.invocable.package_mixin import PackageMixin
from steamship.utils.file_tags import update_file_status
from steamship.utils.text_chunker import chunk_text

DEFAULT_EMBEDDING_INDEX_CONFIG = {
    "embedder": {
        "plugin_handle": "openai-embedder",
        "plugin_instance_handle": "text-embedding-ada-002",
        "fetch_if_exists": True,
        "config": {"model": "text-embedding-ada-002", "dimensionality": 1536},
    }
}

DEFAULT_EMBEDDING_INDEX_HANDLE = "default-embedding-index"


class IndexerMixin(PackageMixin):
    """Provides endpoints for easy Indexing of blockified files."""

    client: Steamship
    context_window_size: int
    context_window_overlap: int
    embedding_index_config: dict

    def __init__(
        self,
        client: Steamship,
        embedder_config: dict = None,
        context_window_size: int = 200,
        context_window_overlap: int = 50,
    ):
        self.client = client
        self.context_window_size = context_window_size
        self.context_window_overlap = context_window_overlap
        self.embedding_indexes = {}
        self.embedding_index_config = embedder_config or DEFAULT_EMBEDDING_INDEX_CONFIG

    def _get_page(self, block: Block) -> Optional[str]:
        """Return the page_id from the block if it exists."""
        page_id = None
        for tag in block.tags:
            if tag.name == DocTag.PAGE:
                page_num = tag.value.get(TagValueKey.NUMBER_VALUE)
                if page_num is not None:
                    page_id = page_num
        return page_id

    def _get_index(self, index_handle: Optional[str] = None) -> EmbeddingIndexPluginInstance:
        """Return the page_id from the block if it exists."""
        handle = index_handle or DEFAULT_EMBEDDING_INDEX_HANDLE
        if handle in self.embedding_indexes:
            return self.embedding_indexes[handle]

        self.embedding_indexes[handle] = cast(
            EmbeddingIndexPluginInstance,
            self.client.use_plugin(
                plugin_handle="embedding-index",
                instance_handle=handle,
                config=self.embedding_index_config,
                fetch_if_exists=True,
            ),
        )
        return self.embedding_indexes[handle]

    @post("/index_text")
    def index_text(
        self, text: str, metadata: Optional[dict] = None, index_handle: Optional[str] = None
    ) -> bool:
        """Load text into an embedding index.

        Optional arguments:
        - index_handle (uses your default index if blank)
        - metadata (returned on embedding results for source attribution)
        """
        tags = []
        for chunk in chunk_text(
            text, chunk_size=self.context_window_size, chunk_overlap=self.context_window_overlap
        ):
            tags.append(Tag(text=chunk, value=metadata))
        self._get_index(index_handle).insert(tags)
        return True

    def _index_block(
        self, block: Block, metadata: Optional[dict] = None, index_handle: Optional[str] = None
    ):
        page_id = self._get_page(block)
        _metadata = {}
        if metadata:
            _metadata.update(metadata)

        _metadata.update(
            {
                "file_id": block.file_id,
                "block_id": block.id,
                "page": page_id,
            }
        )

        return self.index_text(block.text, metadata=_metadata, index_handle=index_handle)

    @post("/index_block")
    def index_block(
        self, block_id: str, metadata: Optional[dict] = None, index_handle: Optional[str] = None
    ):
        """Load a Steamship Block into an embedding index.

        Optional arguments:
        - index_handle (uses your default index if blank)
        - metadata (returned on embedding results for source attribution)
        """
        block = Block.get(self.client, _id=block_id)
        page_id = self._get_page(block)
        _metadata = {}
        _metadata.update(metadata)
        _metadata.update(
            {
                "file_id": block.file_id,
                "block_id": block.id,
                "page": page_id,
            }
        )

        return self.index_text(block.text, metadata=_metadata, index_handle=index_handle)

    @post("/index_file")
    def index_file(
        self, file_id: str, metadata: Optional[dict] = None, index_handle: Optional[str] = None
    ) -> bool:
        """Load a Steamship File into an embedding index.

        Optional arguments:
        - index_handle (uses your default index if blank)
        - metadata (returned on embedding results for source attribution)
        """
        file = File.get(self.client, _id=file_id)
        update_file_status(self.client, file, "Indexing")

        _metadata = {}
        if file.mime_type:
            _metadata["mime_type"] = file.mime_type

        for tag in file.tags or []:
            if tag.kind == TagKind.DOCUMENT and tag.name == DocTag.TITLE:
                if title := tag.value.get(TagValueKey.STRING_VALUE):
                    _metadata["title"] = title

        if metadata:
            _metadata.update(metadata)

        for block in file.blocks or []:
            self._index_block(block, metadata=_metadata, index_handle=index_handle)

        update_file_status(self.client, file, "Indexed")
        return True

    @post("/search_index")
    def search_index(
        self, query: str, index_handle: Optional[str] = None, k: int = 5
    ) -> SearchResults:
        """Search an embedding index.

        Optional arguments:
        - index_handle (uses your default index if blank)
        """
        index = self._get_index(index_handle)
        task = index.search(query, k)
        return task.wait()
