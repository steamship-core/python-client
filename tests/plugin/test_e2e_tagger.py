from tests.client.operations.test_tag_file import tag_file
from ..client.helpers import deploy_plugin, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_tagger():
    client = _steamship()
    with deploy_plugin("plugin_parser.py", "tagger") as (plugin, version, instance):
        test_doc = "Hi there"
        res = client.tag(doc= test_doc, pluginInstance=instance.handle)
        res.wait()
        assert (res.error is None)
        assert (res.data is not None)
        assert (len(res.data.file.blocks) == 1)
        assert (res.data.file.blocks[0].text == test_doc)

        # Let's try it on a file. This is the same test we run on the Swift test parser.
        # Since the python test parser is implemented to behave the same, we can reuse it!
        tag_file(client, instance.handle)
