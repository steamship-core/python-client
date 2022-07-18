from steamship_tests import PLUGINS_PATH
from steamship_tests.client.operations.test_tag_file import tag_file
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client


def test_e2e_tagger():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "taggers" / "plugin_parser.py"
    # TODO (enias): Use Enum for plugin type
    with deploy_plugin(client, parser_path, "tagger") as (plugin, version, instance):
        test_doc = "Hi there"
        res = instance.tag(doc=test_doc)
        res.wait()
        assert res.error is None
        assert res.data is not None
        assert len(res.data.file.blocks) == 1
        assert res.data.file.blocks[0].text == test_doc

        # Let's try it on a file. This is the same test we run on the Swift test parser.
        # Since the python test parser is implemented to behave the same, we can reuse it!
        tag_file(client, instance.handle)
