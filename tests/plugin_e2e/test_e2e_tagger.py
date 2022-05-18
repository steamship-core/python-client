from tests import APPS_PATH
from tests.client.operations.test_tag_file import tag_file
from tests.utils.client import get_steamship_client
from tests.utils.deployables import deploy_plugin


def test_e2e_tagger():
    client = get_steamship_client()
    parser_path = APPS_PATH / "plugins" / "taggers" / "plugin_parser.py"
    # TODO (enias): Use Enum for plugin type
    with deploy_plugin(client, parser_path, "tagger") as (plugin, version, instance):
        test_doc = "Hi there"
        res = client.tag(doc=test_doc, plugin_instance=instance.handle)
        res.wait()
        assert res.error is None
        assert res.data is not None
        assert len(res.data.file.blocks) == 1
        assert res.data.file.blocks[0].text == test_doc

        # Let's try it on a file. This is the same test we run on the Swift test parser.
        # Since the python test parser is implemented to behave the same, we can reuse it!
        tag_file(client, instance.handle)
