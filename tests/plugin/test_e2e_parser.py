from steamship.plugin.parser import ParseRequest
from steamship.plugin.service import PluginRequest

from ..client.helpers import deploy_app, register_app_as_plugin, _steamship
from ..client.test_file_parse import parse_file
from dataclasses import asdict

__copyright__ = "Steamship"
__license__ = "MIT"

TEST_REQ = ParseRequest(
    docs=["Hi there."],
    blockIds=["ABC"]
)
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def test_e2e_embedder():
    client = _steamship()
    with deploy_app("plugin_parser.py") as (app, version, instance):
        with register_app_as_plugin(client, "parser", "parse", app, instance) as plugin:
            res = client.parse(docs=TEST_REQ.docs, plugin=plugin.handle)
            res.wait()
            assert (res.error is None)
            assert (res.data is not None)
            assert (len(res.data.blocks) == 1)
            assert (res.data.blocks[0].text == TEST_REQ.docs[0])

            # Let's try it on a file. This is the same test we run on the Swift test parser.
            # Since the python test parser is implemented to behave the same, we can reuse it!
            parse_file(client, plugin.handle)
