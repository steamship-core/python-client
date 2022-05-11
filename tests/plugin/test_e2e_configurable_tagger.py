import json

from steamship import PluginInstance

__copyright__ = "Steamship"
__license__ = "MIT"

from tests import APPS_PATH
from tests.utils.client import get_steamship_client
from tests.utils.deployables import deploy_plugin


def test_e2e_parser():
    client = get_steamship_client()
    tagger_plugin_path = (
        APPS_PATH / "plugins" / "taggers" / "plugin_configurable_tagger.py"
    )
    config_template = {
        "tagKind": {"type": "string"},
        "tagName": {"type": "string"},
        "numberValue": {"type": "number"},
        "booleanValue": {"type": "boolean"},
    }
    instance_config1 = {
        "tagKind": "testTagKind",
        "tagName": "testTagName",
        "numberValue": 3,
        "booleanValue": True,
    }

    with deploy_plugin(
        client,
        tagger_plugin_path,
        "tagger",
        version_config_template=config_template,
        instance_config=instance_config1,
    ) as (plugin, version, instance):
        test_doc = "Hi there"
        res = client.tag(doc=test_doc, plugin_instance=instance.handle)
        res.wait()
        assert res.error is None
        assert res.data is not None
        assert len(res.data.file.blocks) == 1
        assert res.data.file.blocks[0].text == test_doc

        # Validate configured content
        assert len(res.data.file.tags) == 1
        tag = res.data.file.tags[0]
        assert tag.name == instance_config1["tagName"]
        assert tag.kind == instance_config1["tagKind"]
        tag_value = tag.value
        assert tag_value["numberValue"] == instance_config1["numberValue"]
        assert tag_value["booleanValue"] == instance_config1["booleanValue"]

        instance_config2 = {
            "tagKind": "testTagKind2",
            "tagName": "testTagName2",
            "numberValue": 4,
            "booleanValue": False,
        }

        instance2 = PluginInstance.create(
            client,
            plugin_id=plugin.id,
            plugin_version_id=version.id,
            config=instance_config2,
        )
        instance2.wait()
        assert instance2.error is None
        assert instance2.data is not None
        instance2 = instance2.data

        res = client.tag(doc=test_doc, plugin_instance=instance2.handle)
        res.wait()
        assert res.error is None
        assert res.data is not None
        assert len(res.data.file.blocks) == 1
        assert res.data.file.blocks[0].text == test_doc

        # Validate configured content
        assert len(res.data.file.tags) == 1
        tag = res.data.file.tags[0]
        assert tag.name == instance_config2["tagName"]
        assert tag.kind == instance_config2["tagKind"]
        tag_value = tag.value
        assert tag_value["numberValue"] == instance_config2["numberValue"]
        assert tag_value["booleanValue"] == instance_config2["booleanValue"]
