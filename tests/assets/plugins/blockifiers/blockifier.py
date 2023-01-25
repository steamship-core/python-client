from typing import Type

from steamship import Block, File, Tag
from steamship.data import DocTag, TagKind
from steamship.invocable import Config, InvocableResponse, create_handler
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.blockifier.blockifier import Blockifier
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput

# Note 1: this aligns with the same document in the internal Engine test.
# Note 2: This should be duplicated from the test_importer because of the way our test system will
#         bundle this into an invocable deployment package (importing won't work!)
HANDLE = "test-blockifier-plugin-v1"
TEST_H1 = "A Poem"
TEST_S1 = "Roses are red."
TEST_S2 = "Violets are blue."
TEST_S3 = "Sugar is sweet, and I love you."
TEST_DOC = f"# {TEST_H1}\n\n{TEST_S1} {TEST_S2}\n\n{TEST_S3}\n"


class DummyBlockifierPlugin(Blockifier):
    class DummyBlockifierConfig(Config):
        pass

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return cls.DummyBlockifierConfig

    def run(
        self, request: PluginRequest[RawDataPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        return InvocableResponse(
            data=BlockAndTagPluginOutput(
                file=File(
                    blocks=[
                        Block(
                            text=TEST_H1,
                            tags=[Tag(kind=TagKind.DOCUMENT, name=DocTag.H1)],
                        ),
                        Block(
                            text=TEST_S1,
                            tags=[Tag(kind=TagKind.DOCUMENT, name=DocTag.SENTENCE)],
                        ),
                        Block(
                            text=TEST_S2,
                            tags=[Tag(kind=TagKind.DOCUMENT, name=DocTag.SENTENCE)],
                        ),
                        Block(
                            text=TEST_S3,
                            tags=[Tag(kind=TagKind.DOCUMENT, name=DocTag.PARAGRAPH)],
                        ),
                    ]
                )
            )
        )


handler = create_handler(DummyBlockifierPlugin)
