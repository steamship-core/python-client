import pytest
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.client import steamship_use_skill
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import SteamshipError
from steamship.client.steamship import SKILL_TO_PROVIDER


def test_use_skill():
    client = get_steamship_client()
    tagger_plugin_path = PLUGINS_PATH / "taggers" / "plugin_configurable_tagger.py"
    config_template = {
        "tagKind": {"type": "string"},
        "tagName": {"type": "string"},
        "numberValue": {"type": "number"},
        "booleanValue": {"type": "boolean"},
    }
    instance_config1 = {
        "tagKind": "testTagKind",
        "tagName": "testTagName",
        "numberValue": 5,
        "booleanValue": True,
    }

    with deploy_plugin(
        client,
        tagger_plugin_path,
        "tagger",
        version_config_template=config_template,
        instance_config=instance_config1,
    ) as (plugin, version, instance):
        plugin_handle = plugin.handle

        SKILL_TO_PROVIDER["hello"] = {
            "steamship": {
                "plugin_handle": plugin_handle,
                "config": {
                    "tagKind": "testTagKind2",
                    "tagName": "testTagName2",
                    "numberValue": 4,
                    "booleanValue": False,
                },
            }
        }

        test_str = "Hi there!"
        with pytest.raises(SteamshipError):
            with steamship_use_skill(skill="doesnotexist"):
                pass

        with pytest.raises(SteamshipError):
            with steamship_use_skill(skill="hello", provider="doesnotexist"):
                pass

        with steamship_use_skill(skill="hello", delete_workspace=False) as skill_instance_1:
            _test_skill_instance(skill_instance_1, test_str)

        with steamship_use_skill(
            skill="hello", provider="steamship", delete_workspace=False
        ) as skill_instance_1:
            _test_skill_instance(skill_instance_1, test_str)


def _test_skill_instance(skill_instance_1, test_str):
    assert skill_instance_1 is not None
    res = skill_instance_1.tag(doc=test_str)
    res.wait()
    assert res.output is not None
    assert len(res.output.file.blocks) == 1
    assert res.output.file.blocks[0].text == test_str
    # Validate configured content
    assert len(res.output.file.tags) == 1
    tag = res.output.file.tags[0]
    config = SKILL_TO_PROVIDER["hello"]["steamship"]["config"]
    assert tag.name == config["tagName"]
    assert tag.kind == config["tagKind"]
    assert tag.value["numberValue"] == config["numberValue"]
    assert tag.value["booleanValue"] == config["booleanValue"]
