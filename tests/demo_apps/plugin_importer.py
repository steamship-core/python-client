from steamship.app import App, post, create_lambda_handler
from steamship.plugin.importer import Importer, ImportResponse, ImportRequest
from steamship.plugin.service import PluginResponse, PluginRequest

# Note: this aligns with the same document in the internal Engine test.
NAME = "Test Importer (Plugin)"
HANDLE = "test-importer-plugin-v1"
URL = "builtin://importer/test-plugin/v1"
TEST_H1 = "A Poem"
TEST_S1 = "Roses are red."
TEST_S2 = "Violets are blue."
TEST_S3 = "Sugar is sweet, and I love you."
TEST_DOC = "# {}\n\n{} {}\n\n{}\n".format(TEST_H1, TEST_S1, TEST_S2, TEST_S3)


class TestImporterPlugin(Importer, App):
    def run(self, request: PluginRequest[ImportRequest]) -> PluginResponse[ImportResponse]:
        return PluginResponse(
            data=ImportResponse(
                string=TEST_DOC
            )
        )

    @post('do_import')
    def do_import(self, **kwargs) -> any:
        importRequest = self.__class__.parse_request(request=kwargs)
        importResponse = self.run(importRequest)
        return self.__class__.response_to_dict(importResponse)


handler = create_lambda_handler(TestImporterPlugin)
