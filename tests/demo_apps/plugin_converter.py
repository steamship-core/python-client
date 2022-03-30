from steamship import Block, File, DocTag
from steamship.app import App, post, create_handler, Response
from steamship.plugin.converter import Converter, ConvertResponse, ConvertRequest
from steamship.plugin.service import PluginResponse, PluginRequest

# Note 1: this aligns with the same document in the internal Engine test.
# Note 2: This should be duplicated from the test_importer because of the way our test system will
#         bundle this into an app deployment package (importing won't work!)
NAME = "Test Converter (Plugin)"
HANDLE = "test-converter-plugin-v1"
URL = "builtin://converter/test-plugin/v1"
TEST_H1 = "A Poem"
TEST_S1 = "Roses are red."
TEST_S2 = "Violets are blue."
TEST_S3 = "Sugar is sweet, and I love you."
TEST_DOC = "# {}\n\n{} {}\n\n{}\n".format(TEST_H1, TEST_S1, TEST_S2, TEST_S3)


class TestConverterPlugin(Converter, App):
    def run(self, request: PluginRequest[ConvertRequest]) -> PluginResponse[ConvertResponse]:
        return PluginResponse(data=ConvertResponse(file=File(
            blocks=[
                Block(text=TEST_H1, type=DocTag.h1),
                Block(type=DocTag.paragraph),
                Block(text=TEST_S1, type=DocTag.sentence),
                Block(text=TEST_S2, type=DocTag.sentence),
                Block(type=DocTag.paragraph, text=TEST_S3)
            ]
        )))

    @post('convert')
    def convert(self, **kwargs) -> Response:
        convertRequest = Converter.parse_request(request=kwargs)
        convertResponse = self.run(convertRequest)
        ret = Converter.response_to_dict(convertResponse)
        return Response(json=ret)


handler = create_handler(TestConverterPlugin)
