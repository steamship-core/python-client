from steamship import File
from steamship.invocable import PackageService, post
from steamship.invocable.mixins.indexer_pipeline_mixin import IndexerPipelineMixin


class PackageWithIndexerPipelineMixin(PackageService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_mixin(IndexerPipelineMixin(self.client, self))

    @post("get_file")
    def get_file(self, id: str) -> File:
        file = File.get(self.client, _id=id)
        return file
