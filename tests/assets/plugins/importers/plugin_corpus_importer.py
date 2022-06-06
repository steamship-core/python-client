from typing import Type

from steamship import File
from steamship.app import Response, create_handler
from steamship.data.operations.corpus_importer import CorpusImportRequest, CorpusImportResponse
from steamship.plugin.config import Config
from steamship.plugin.corpus_importer import CorpusImporter
from steamship.plugin.service import PluginRequest


class TestCorpusImporterPlugin(CorpusImporter):
    class EmptyConfig(Config):
        pass

    def config_cls(self) -> Type[Config]:
        return self.EmptyConfig

    def run(self, request: PluginRequest[CorpusImportRequest]) -> Response[CorpusImportResponse]:
        return Response(
            data=CorpusImportResponse(
                file_import_requests=[
                    File.CreateRequest(
                        type="fileImporter",
                        corpusId=request.data.url,
                        plugin_instance=request.data.file_importer_plugin_instance
                        # This is a test importer built into the Steamship Engine
                    ),
                    File.CreateRequest(
                        type="fileImporter",
                        corpusId=request.data.url,
                        plugin_instance=request.data.file_importer_plugin_instance,
                    ),
                ]
            )
        )


handler = create_handler(TestCorpusImporterPlugin)
