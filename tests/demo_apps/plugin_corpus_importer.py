from steamship.app import App, post, create_handler
from steamship.plugin.corpus_importer import CorpusImporter, CorpusImportResponse, CorpusImportRequest
from steamship.plugin.file_importer import FileImportRequest
from steamship.plugin.service import PluginResponse, PluginRequest


class TestCorpusImporterPlugin(CorpusImporter, App):
    def run(self, request: PluginRequest[CorpusImportRequest]) -> PluginResponse[CorpusImportResponse]:
        return PluginResponse(
            data=CorpusImportResponse(
                fileImportRequests=[
                    FileImportRequest(
                        type="fileImporter",
                        plugin="test-fileImporter-valueOrData-v1"
                        # This is a test importer built into the Steamship Engine
                    ),
                    FileImportRequest(
                        type="fileImporter",
                        plugin="test-fileImporter-valueOrData-v1"
                    )
                ]
            )
        )

    @post('do_import')
    def do_import(self, **kwargs) -> any:
        request = CorpusImporter.parse_request(request=kwargs)
        response = self.run(request)
        return CorpusImporter.response_to_dict(response)


handler = create_handler(TestCorpusImporterPlugin)
