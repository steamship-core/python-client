from steamship.app import App, post, create_handler
from steamship.plugin.file_importer import FileImporter
from steamship.plugin.service import PluginResponse, PluginRequest
from steamship.extension.file import File

# Note: this aligns with the same document in the internal Engine test.
NAME = "Test Importer (Plugin)"
HANDLE = "test-importer-plugin-v1"
URL = "builtin://importer/test-plugin/v1"
TEST_H1 = "A Poem"
TEST_S1 = "Roses are red."
TEST_S2 = "Violets are blue."
TEST_S3 = "Sugar is sweet, and I love you."
TEST_DOC = "# {}\n\n{} {}\n\n{}\n".format(TEST_H1, TEST_S1, TEST_S2, TEST_S3)


class TestFileImporterPlugin(FileImporter, App):
    def run(self, request: PluginRequest[File.CreateRequest]) -> PluginResponse[File.CreateResponse]:
        return PluginResponse(
            data=File.CreateResponse(
                string=TEST_DOC
            )
        )

    @post('import')
    def do_import(self, **kwargs) -> any:
        importRequest = FileImporter.parse_request(request=kwargs)
        importResponse = self.run(importRequest)
        return FileImporter.response_to_dict(importResponse)


handler = create_handler(TestFileImporterPlugin)
