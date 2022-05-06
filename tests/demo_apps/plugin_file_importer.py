from steamship import MimeTypes
from steamship.deployable import App, post, create_handler, Response
from steamship.plugin.file_importer import FileImporter
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.extension.file import File

# Note: this aligns with the same document in the internal Engine test.
HANDLE = "test-importer-plugin-v1"
TEST_H1 = "A Poem"
TEST_S1 = "Roses are red."
TEST_S2 = "Violets are blue."
TEST_S3 = "Sugar is sweet, and I love you."
TEST_DOC = "# {}\n\n{} {}\n\n{}\n".format(TEST_H1, TEST_S1, TEST_S2, TEST_S3)


class TestFileImporterPlugin(FileImporter, App):
    def run(self, request: PluginRequest[File.CreateRequest]) -> Response[RawDataPluginOutput]:
        return Response(
            data=RawDataPluginOutput(
                string=TEST_DOC,
                mimeType=MimeTypes.MKD
            )
        )

    @post('import')
    def do_import(self, **kwargs) -> any:
        importRequest = FileImporter.parse_request(request=kwargs)
        return self.run(importRequest)


handler = create_handler(TestFileImporterPlugin)
