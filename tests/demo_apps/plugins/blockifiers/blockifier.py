from steamship import Block, File, Tag
from steamship.app import App, Response, create_handler, post
from steamship.data.tags import DocTag, TagKind
from steamship.plugin.blockifier import Blockifier
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest

# Note 1: this aligns with the same document in the internal Engine test.
# Note 2: This should be duplicated from the test_importer because of the way our test system will
#         bundle this into an app deployment package (importing won't work!)
HANDLE = "test-blockifier-plugin-v1"
TEST_H1 = "A Poem"
TEST_S1 = "Roses are red."
TEST_S2 = "Violets are blue."
TEST_S3 = "Sugar is sweet, and I love you."
TEST_DOC = f"# {TEST_H1}\n\n{TEST_S1} {TEST_S2}\n\n{TEST_S3}\n"


class DummyBlockifierPlugin(Blockifier, App):
    def run(
        self, request: PluginRequest[RawDataPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        file = File.CreateRequest(blocks=[])
        for text, tag in {
            (TEST_H1, DocTag.h1),
            (TEST_S1, DocTag.sentence),
            (TEST_S2, DocTag.sentence),
            (TEST_S3, DocTag.paragraph),
        }:
            block = Block.CreateRequest(
                text=text,
                tags=[Tag.CreateRequest(kind=TagKind.doc, name=tag)],
            )
            file.blocks.append(block)
        return Response(data=BlockAndTagPluginOutput(file=file))

    @post("blockify")
    def blockify(self, **kwargs) -> Response:
        blockify_request = Blockifier.parse_request(request=kwargs)
        return self.run(blockify_request)


handler = create_handler(DummyBlockifierPlugin)
