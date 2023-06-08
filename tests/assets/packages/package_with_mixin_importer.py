from steamship import File
from steamship.invocable import PackageService, post
from steamship.invocable.mixins.blockifier_mixin import BlockifierMixin
from steamship.invocable.mixins.file_importer_mixin import FileImporterMixin
from steamship.invocable.mixins.indexer_mixin import IndexerMixin


class PackageWithImporterMixin(PackageService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_mixin(FileImporterMixin(self.client))
        self.add_mixin(BlockifierMixin(self.client))
        self.add_mixin(IndexerMixin(self.client))

    @post("get_file")
    def get_file(self, id: str) -> File:
        file = File.get(self.client, _id=id)
        return file
