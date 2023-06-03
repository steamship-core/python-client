from typing import Optional

from steamship import Steamship
from steamship.invocable import post
from steamship.invocable.mixins.blockifier_mixin import BlockifierMixin
from steamship.invocable.mixins.file_importer_mixin import FileImporterMixin
from steamship.invocable.mixins.indexer_mixin import IndexerMixin
from steamship.invocable.package_mixin import PackageMixin


class IndexerPipelineMixin(PackageMixin):
    """Provides a complete set of endpoints & async workflow for Document Question Answering.

    This Mixin is an async orchestrator of other mixins:
    - Importer Mixin:       to import files, e.g. YouTube videos, PDF urls
    - Blockifier Mixin:     to convert files to Blocks -- whether that's s2t or PDF parsing, etc.
    - Indexer Mixin:        to convert Steamship Files to embedded sharts

    """

    client: Steamship
    blockifier_mixin: BlockifierMixin
    importer_mixin: FileImporterMixin
    indexer_mixin: IndexerMixin

    def __init__(
        self,
        client: Steamship,
    ):
        self.client = client
        self.blockifier_mixin = BlockifierMixin(client)
        self.importer_mixin = FileImporterMixin(client)
        self.indexer_mixin = IndexerMixin(client)

    @post("/index_url")
    def index_url(
        self, url: str, metadata: Optional[dict] = None, index_handle: Optional[str] = None
    ) -> bool:
        pass
