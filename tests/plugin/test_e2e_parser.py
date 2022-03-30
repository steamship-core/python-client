from steamship.plugin.tagger import TagRequest
from steamship.plugin.service import PluginRequest

from ..client.helpers import deploy_plugin, _steamship
from ..client.test_file_parse import parse_file

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
        res = client.parse(docs=TEST_REQ.docs, pluginInstance=plugin.handle)
        res.wait()
        assert (res.error is None)
        assert (res.data is not None)
        assert (len(res.data.blocks) == 1)
        assert (res.data.blocks[0].text == TEST_REQ.docs[0])

        # Let's try it on a file. This is the same test we run on the Swift test parser.
        # Since the python test parser is implemented to behave the same, we can reuse it!
        parse_file(client, plugin.handle)
