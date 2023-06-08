from typing import Optional

from steamship import File, Steamship, Task
from steamship.invocable import PackageService, post
from steamship.invocable.mixins.blockifier_mixin import BlockifierMixin
from steamship.invocable.mixins.file_importer_mixin import FileImporterMixin
from steamship.invocable.mixins.indexer_mixin import IndexerMixin
from steamship.invocable.package_mixin import PackageMixin
from steamship.utils.file_tags import update_file_status


class IndexerPipelineMixin(PackageMixin):
    """Provides a complete set of endpoints & async workflow for Document Question Answering.

    This Mixin is an async orchestrator of other mixins:
    - Importer Mixin:       to import files, e.g. YouTube videos, PDF urls
    - Blockifier Mixin:     to convert files to Blocks -- whether that's s2t or PDF parsing, etc.
    - Indexer Mixin:        to convert Steamship Files to embedded sharts

    """

    client: Steamship
    invocable: PackageService
    blockifier_mixin: BlockifierMixin
    importer_mixin: FileImporterMixin
    indexer_mixin: IndexerMixin

    def __init__(self, client: Steamship, invocable: PackageService):
        self.client = client
        self.invocable = invocable

        self.importer_mixin = FileImporterMixin(client)
        self.invocable.add_mixin(self.importer_mixin)

        self.blockifier_mixin = BlockifierMixin(client)
        self.invocable.add_mixin(self.blockifier_mixin)

        self.indexer_mixin = IndexerMixin(client)
        self.invocable.add_mixin(self.indexer_mixin)

    @post("/set_file_status")
    def set_file_status(self, file_id: str, status: str) -> bool:
        """Set the status bit of a file. Intended to be scheduled after import."""
        file = File.get(self.client, _id=file_id)
        update_file_status(self.client, file, status)
        return True

    @post("/index_url")
    def index_url(
        self,
        url: str,
        metadata: Optional[dict] = None,
        index_handle: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Task:
        # Step 1: Import the URL
        file, task = self.importer_mixin.import_url_to_file_and_task(url)

        # Step 2: Blockify the File
        importer_task_id = None
        if task and task.task_id:
            importer_task_id = task.task_id

        blockify_task = self.blockifier_mixin.blockify(
            file_id=file.id, mime_type=mime_type, after_task_id=importer_task_id
        )

        # Step 3: Index the File
        index_task = self.invocable.invoke_later(
            method="index_file",
            wait_on_tasks=[blockify_task],
            arguments={
                "file_id": file.id,
                "index_handle": index_handle,
            },
        )

        # Step 4: Set the File Status to 'indexed'
        self.invocable.invoke_later(
            method="set_file_status",
            wait_on_tasks=[index_task],
            arguments={
                "file_id": file.id,
                "status": "Indexed",
            },
        )

        # We return the index task instead of the file set task just to safe a few seconds.
        return index_task
