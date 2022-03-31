from steamship import File
from steamship.app import App, post, create_handler
from steamship.client.operations.corpus_importer import CorpusImportRequest, CorpusImportResponse
from steamship.plugin.corpus_importer import CorpusImporter
from steamship.plugin.service import PluginResponse, PluginRequest


class TestCorpusImporterPlugin(CorpusImporter, App):
    def run(self, request: PluginRequest[CorpusImportRequest]) -> PluginResponse[CorpusImportResponse]:
        return PluginResponse(
            data=CorpusImportResponse(
                fileImportRequests=[
                    File.CreateRequest(
                        type="fileImporter",
                        pluginInstance=request.data.fileImporterPluginInstance
                        # This is a test importer built into the Steamship Engine
                    ),
                    File.CreateRequest(
                        type="fileImporter",
                        pluginInstance=request.data.fileImporterPluginInstance
                    )
                ]
            )
        )

    @post('import')
    def do_import(self, **kwargs) -> any:
        request = CorpusImporter.parse_request(request=kwargs)
        response = self.run(request)
        return CorpusImporter.response_to_dict(response)


handler = create_handler(TestCorpusImporterPlugin)
