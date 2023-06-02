from steamship import File
from steamship.invocable import PackageService, post
from steamship.invocable.mixins.file_importer_mixin import FileImporterMixin


class PackageWithImporterMixin(PackageService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_mixin(FileImporterMixin(self.client))

    @post("get_file")
    def get_file(self, id: str) -> File:
        file = File.get(self.client, _id=id)
        return file
