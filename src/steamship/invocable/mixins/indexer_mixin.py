from typing import Optional

from steamship import Block, DocTag, File, Steamship, Tag, Task
from steamship.data import TagValueKey
from steamship.data.plugin.index_plugin_instance import EmbeddingIndexPluginInstance
from steamship.invocable import post
from steamship.invocable.package_mixin import PackageMixin
from steamship.utils.file_tags import update_file_status


class FlileIndexerMixin(PackageMixin):
    """Provides endpoints for easy Indexing of blockified files."""

    client: Steamship
    context_window_size: int
    context_window_overlap: int
    embedding_index_handle: str
    embedding_index: Optional[EmbeddingIndexPluginInstance]

    def __init__(
        self, client: Steamship, embedding_index_handle: str, context_window_size: int = 100
    ):
        self.client = client
        self.context_window_size = context_window_size
        self.embedding_index_handle = embedding_index_handle
        self.embedding_index = None

    def _get_page(self, block: Block) -> Optional[str]:
        """Return the page_id from the block if it exists."""
        page_id = None
        for tag in block.tags:
            if tag.name == DocTag.PAGE:
                page_num = tag.value.get(TagValueKey.NUMBER_VALUE)
                if page_num is not None:
                    page_id = page_num
        return page_id

    def _get_index(self, block: Block) -> EmbeddingIndexPluginInstance:
        """Return the page_id from the block if it exists."""
        if self.embedding_index:
            return self.embedding_index

        # TODO: Load

    def index_block(self, block: Block):
        page_id = self._get_page(block)

        tags = []
        for i in range(0, len(block.text), self.context_window_size):
            # Calculate the extent of the window plus the overlap at the edges
            min_range = max(0, i - self.context_window_overlap)
            max_range = i + self.context_window_size + self.context_window_overlap

            # Get the text covering that chunk.
            chunk = block.text[min_range:max_range]

            tag = Tag(
                text=chunk,
                metadata={
                    "source": "",
                    "file_id": block.file_id,
                    "block_id": block.id,
                    "page": page_id,
                },
            )
            tags.append(tags)

        self._get_index().insert(tags)

    @post("/index_file")
    def index_file(
        self,
        file_id: str,
    ) -> Task:
        file = File.get(self.client, _id=file_id)
        update_file_status(file, "Indexing")

        # For PDFs, we iterate over the blocks (block = page) and then split each chunk of texts into the context
        # window units.

        documents = []

        for block in file.blocks:
            self.index_block(block)

        # self._get_index().add_documents(documents)
        # self._update_file_status(file, "Indexed")
        # return True
