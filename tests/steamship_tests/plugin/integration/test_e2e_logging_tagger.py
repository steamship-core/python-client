from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client


def test_e2e_tagger():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "taggers" / "plugin_logging_tagger.py"
    with deploy_plugin(client, parser_path, "tagger") as (plugin, version, instance):
        test_doc = "Hi there"
        res = instance.tag(doc=test_doc)
        res.wait()
        assert res.output is not None
        assert len(res.output.file.blocks) == 1
        assert res.output.file.blocks[0].text == test_doc
