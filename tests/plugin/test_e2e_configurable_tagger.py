import json

from steamship import PluginInstance
from ..client.helpers import deploy_plugin, _steamship
from tests.client.operations.test_tag_file import parse_file

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_parser():
    client = _steamship()

    configTemplate = {"tagKind": {"type":"string"},
                    "tagName": {"type":"string"},
                    "numberValue": {"type":"number"},
                    "booleanValue": {"type":"boolean"}}
    instanceConfig1 = {"tagKind": "testTagKind",
                         "tagName": "testTagName",
                        "numberValue": 3,
                        "booleanValue": True}

    with deploy_plugin("plugin_configurable_tagger.py", "tagger", versionConfigTemplate=configTemplate, instanceConfig=instanceConfig1) as (plugin, version, instance):
        test_doc = "Hi there"
        res = client.tag(doc=test_doc, pluginInstance=instance.handle)
        res.wait()
        assert (res.error is None)
        assert (res.data is not None)
        assert (len(res.data.file.blocks) == 1)
        assert (res.data.file.blocks[0].text == test_doc)

        #Validate configured content
        assert (len(res.data.file.tags) == 1)
        tag = res.data.file.tags[0]
        assert (tag.name == instanceConfig1['tagName'])
        assert (tag.kind == instanceConfig1['tagKind'])
        tagValue = json.loads(tag.value)
        assert (tagValue['numberValue'] == instanceConfig1['numberValue'])
        assert (tagValue['booleanValue'] == instanceConfig1['booleanValue'])

        instanceConfig2 = {"tagKind": "testTagKind2",
                           "tagName": "testTagName2",
                           "numberValue": 4,
                           "booleanValue": False}

        instance2 = PluginInstance.create(
            client,
            pluginId=plugin.id,
            pluginVersionId=version.id,
            config=instanceConfig2
        )
        instance2.wait()
        assert (instance2.error is None)
        assert (instance2.data is not None)
        instance2 = instance2.data

        res = client.tag(doc=test_doc, pluginInstance=instance2.handle)
        res.wait()
        assert (res.error is None)
        assert (res.data is not None)
        assert (len(res.data.file.blocks) == 1)
        assert (res.data.file.blocks[0].text == test_doc)

        # Validate configured content
        assert (len(res.data.file.tags) == 1)
        tag = res.data.file.tags[0]
        assert (tag.name == instanceConfig2['tagName'])
        assert (tag.kind == instanceConfig2['tagKind'])
        tagValue = json.loads(tag.value)
        assert (tagValue['numberValue'] == instanceConfig2['numberValue'])
        assert (tagValue['booleanValue'] == instanceConfig2['booleanValue'])






