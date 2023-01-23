from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import PluginInstance
from steamship.data import TagValueKey


def test_e2e_parser():
    client = get_steamship_client()
    tagger_plugin_path = PLUGINS_PATH / "taggers" / "plugin_configurable_tagger.py"
    config_template = {
        "tagKind": {"type": "string"},
        "tagName": {"type": "string"},
        "numberValue": {"type": "number"},
        "booleanValue": {"type": "boolean"},
        "stringValue": {"type": "string"},
    }
    instance_config1 = {
        "tagKind": "testTagKind",
        "tagName": "testTagName",
        "numberValue": 3,
        "booleanValue": True,
        "stringValue": "Hi",
    }

    with deploy_plugin(
        client,
        tagger_plugin_path,
        "tagger",
        version_config_template=config_template,
        instance_config=instance_config1,
    ) as (plugin, version, instance):
        test_doc = "Hi there"
        res = instance.tag(doc=test_doc)
        res.wait()
        assert res.output is not None
        assert len(res.output.file.blocks) == 1
        assert res.output.file.blocks[0].text == test_doc

        # Validate configured content
        assert len(res.output.file.tags) == 1
        tag = res.output.file.tags[0]
        assert tag.name == instance_config1["tagName"]
        assert tag.kind == instance_config1["tagKind"]
        tag_value = tag.value
        assert tag_value[TagValueKey.NUMBER_VALUE] == instance_config1["numberValue"]
        assert tag_value[TagValueKey.BOOL_VALUE] == instance_config1["booleanValue"]
        assert tag_value[TagValueKey.STRING_VALUE] == instance_config1["stringValue"]

        instance_config2 = {
            "tagKind": "testTagKind2",
            "tagName": "testTagName2",
            "numberValue": 4,
            "booleanValue": False,
            "stringValue": "Hi",
        }

        instance2 = PluginInstance.create(
            client,
            plugin_id=plugin.id,
            plugin_version_id=version.id,
            config=instance_config2,
        )
        assert instance2 is not None

        res = instance2.tag(doc=test_doc)
        res.wait()
        assert res.output is not None
        assert len(res.output.file.blocks) == 1
        assert res.output.file.blocks[0].text == test_doc

        # Validate configured content
        assert len(res.output.file.tags) == 1
        tag = res.output.file.tags[0]
        assert tag.name == instance_config2["tagName"]
        assert tag.kind == instance_config2["tagKind"]
        tag_value = tag.value
        assert tag_value[TagValueKey.NUMBER_VALUE] == instance_config2["numberValue"]
        assert tag_value[TagValueKey.BOOL_VALUE] == instance_config2["booleanValue"]
        assert tag_value[TagValueKey.STRING_VALUE] == instance_config2["stringValue"]
