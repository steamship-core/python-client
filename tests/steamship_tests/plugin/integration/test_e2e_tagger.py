import pytest
from steamship_tests import PLUGINS_PATH
from steamship_tests.client.operations.test_tag_file import tag_file
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import SteamshipError


def test_e2e_tagger():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "taggers" / "plugin_parser.py"
    # TODO (enias): Use Enum for plugin type
    with deploy_plugin(client, parser_path, "tagger") as (
        plugin,
        version,
        instance,
    ):
        test_doc = "Hi there"
        res = instance.tag(doc=test_doc)
        res.wait()
        assert res.output is not None
        assert len(res.output.file.blocks) == 1
        assert res.output.file.blocks[0].text == test_doc

        # Let's try it on a file. This is the same test we run on the Swift test parser.
        # Since the python test parser is implemented to behave the same, we can reuse it!
        tag_file(client, instance.handle)


def test_e2e_tagger_bad_import():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "taggers" / "plugin_tagger_bad_import.pyignore"
    # TODO (enias): Use Enum for plugin type

    with pytest.raises(SteamshipError) as error:
        with deploy_plugin(client, parser_path, "tagger") as (
            plugin,
            version,
            instance,
        ):
            pass  # Shouldn't get here!

    assert error is not None
    assert "No module named 'somethingthatclearlydoesnotexist'" in error.value.message
