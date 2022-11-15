from steamship import MimeTypes
from steamship.invocable import InvocableResponse, create_handler
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.file_importer import FileImporter
from steamship.plugin.inputs.file_import_plugin_input import FileImportPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput

# Note: this aligns with the same document in the internal Engine test.
HANDLE = "test-importer-plugin-v1"
TEST_H1 = "A Poem"
TEST_S1 = "Roses are red."
TEST_S2 = "Violets are blue."
TEST_S3 = "Sugar is sweet, and I love you."
TEST_DOC = f"# {TEST_H1}\n\n{TEST_S1} {TEST_S2}\n\n{TEST_S3}\n"


class TestFileImporterPlugin(FileImporter):
    def run(
        self, request: PluginRequest[FileImportPluginInput]
    ) -> InvocableResponse[RawDataPluginOutput]:
        return InvocableResponse(data=RawDataPluginOutput(string=TEST_DOC, mime_type=MimeTypes.MKD))


handler = create_handler(TestFileImporterPlugin)
