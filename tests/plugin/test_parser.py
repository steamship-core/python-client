from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest, PluginResponse
from steamship.extension.file import File
from steamship.data.block import Block

__copyright__ = "Steamship"
__license__ = "MIT"

from ..demo_apps.plugin_parser import TestParserPlugin

TEST_REQ = BlockAndTagPluginInput(
    file=File(
        blocks=[
            Block(id='ABC', text='Once upon a time there was a magical ship. The ship was powered by STEAM. The ship went to the moon.' )
        ]
    )
)
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def _test_resp(res):
    assert (type(res) == PluginResponse)
    assert (type(res.data) == BlockAndTagPluginOutput)
    assert (len(res.data.file.blocks) == 1)
    assert (res.data.file.blocks[0].text == TEST_REQ.file.blocks[0].text)
    assert (len(res.data.file.blocks[0].tags) == 3)


def test_parser():
    parser = TestParserPlugin()
    res = parser.run(TEST_PLUGIN_REQ)
    _test_resp(res)
