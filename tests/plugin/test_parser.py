from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.service import PluginRequest, PluginResponse
from steamship.extension.file import File
from steamship.data.block import Block

__copyright__ = "Steamship"
__license__ = "MIT"

from ..demo_apps.plugin_parser import TestParserPlugin

TEST_REQ = BlockAndTagPluginInput(
    file=File.CreateRequest(
        value="Hi there.",
        blocks=[
            Block.CreateRequest(id='ABC')
        ]
    )
)
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def _test_resp(res):
    assert (type(res) == PluginResponse)
    assert (type(res.data) == TagResponse)
    assert (len(res.data.blocks) == 1)
    assert (res.data.blocks[0].text == TEST_REQ.docs[0])


def test_parser():
    parser = TestParserPlugin()
    res = parser.run(TEST_PLUGIN_REQ)
    _test_resp(res)
