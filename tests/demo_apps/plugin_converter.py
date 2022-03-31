from steamship import Block, File, DocTag, Tag
from steamship.data.tags import TagKind, DocTag
from steamship.app import App, post, create_handler, Response
from steamship.plugin.converter import Converter
from steamship.plugin.service import PluginResponse, PluginRequest
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput

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
    def run(self, request: PluginRequest[RawDataPluginInput]) -> PluginResponse[BlockAndTagPluginOutput]:
        return PluginResponse(data=BlockAndTagPluginOutput(file=File.CreateRequest(
            blocks=[
                Block.CreateRequest(text=TEST_H1, tags=[Tag.CreateRequest(kind=TagKind.doc, name=DocTag.h1)]),
                Block.CreateRequest(text=TEST_S1, tags=[Tag.CreateRequest(kind=TagKind.doc, name=DocTag.sentence)]),
                Block.CreateRequest(text=TEST_S2, tags=[Tag.CreateRequest(kind=TagKind.doc, name=DocTag.sentence)]),
                Block.CreateRequest(text=TEST_S3, tags=[Tag.CreateRequest(kind=TagKind.doc, name=DocTag.paragraph)])
            ]
        )))

    @post('convert')
    def convert(self, **kwargs) -> Response:
        rawDataPluginInput = Converter.parse_request(request=kwargs)
        blockAndTagPluginOutput = self.run(rawDataPluginInput)
        ret = Converter.response_to_dict(blockAndTagPluginOutput)
        return Response(json=ret)


handler = create_handler(TestConverterPlugin)
