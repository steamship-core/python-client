from steamship.extension.file import File
from steamship.data.block import Block
from steamship.plugin.service import PluginRequest
from steamship.client.operations.tagger import TagRequest

from ..client.helpers import deploy_plugin, _steamship
from tests.client.operations.test_tag_file import parse_file

__copyright__ = "Steamship"
__license__ = "MIT"

TEST_REQ = TagRequest(
    docs=["Hi there."],
    blockIds=["ABC"]
)
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def test_e2e_parser():
    client = _steamship()
    with deploy_plugin("plugin_parser.py", "tagger") as (plugin, version, instance):
        res = client.tag(doc=TEST_REQ.docs[0], pluginInstance=instance.handle)
        res.wait()
        assert (res.error is None)
        assert (res.data is not None)
        assert (len(res.data.blocks) == 1)
        assert (res.data.blocks[0].text == TEST_REQ.docs[0])

        # Let's try it on a file. This is the same test we run on the Swift test parser.
        # Since the python test parser is implemented to behave the same, we can reuse it!
        parse_file(client, plugin.handle)
