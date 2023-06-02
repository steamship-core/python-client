from steamship import DocTag, File, Steamship, Tag, Task
from steamship.data import TagValueKey
from steamship.invocable import post
from steamship.invocable.package_mixin import PackageMixin


class FlileIndexerMixin(PackageMixin):
    """Provides endpoints for easy Indexing of blockified files."""

    client: Steamship

    def __init__(self, client: Steamship):
        self.client = client

    @post("/index_file")
    def index_file(
        self,
        file_id: str,
    ) -> Task:
        file = File.get(self.client, _id=file_id)
        self._update_file_status(file, "Indexing")

        # For PDFs, we iterate over the blocks (block = page) and then split each chunk of texts into the context
        # window units.

        documents = []

        for block in file.blocks:
            # Load the page_id from the block if it exists
            page_id = None
            for tag in block.tags:
                if tag.name == DocTag.PAGE:
                    page_num = tag.value.get(TagValueKey.NUMBER_VALUE)
                    if page_num is not None:
                        page_id = page_num

            for i in range(0, len(block.text), self.config.context_window_size):
                # Calculate the extent of the window plus the overlap at the edges
                min_range = max(0, i - self.config.context_window_overlap)
                max_range = i + self.config.context_window_size + self.config.context_window_overlap

                # Get the text covering that chunk.
                chunk = block.text[min_range:max_range]

                # Create a Document.
                # TODO(ted): See if there's a way to support the LC Embedding Index abstraction that lets us use Tag here.
                doc = Tag(
                    text=chunk,
                    metadata={
                        "source": "",
                        "file_id": file.id,
                        "block_id": block.id,
                        "page": page_id,
                    },
                )
                documents.append(doc)

        # self._get_index().add_documents(documents)
        # self._update_file_status(file, "Indexed")
        # return True
