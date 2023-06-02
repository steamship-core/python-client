from steamship import Steamship, Task
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
        pass
