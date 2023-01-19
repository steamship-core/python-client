from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.client import steamship_use_plugin
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship.client.steamship import Steamship
from steamship.data import TagKind
from steamship.data.plugin.prompt_generation_plugin_instance import PromptGenerationPluginInstance


def test_use_prompt():
    fixed_prompt_response = "You can tune a guitar, but you can't guitar a tuna!"

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
        "tagKind": TagKind.GENERATION.value,
        "tagName": "testTagName",
        "numberValue": 3,
        "booleanValue": True,
        "stringValue": fixed_prompt_response,
    }

    with deploy_plugin(
        client,
        tagger_plugin_path,
        "tagger",
        version_config_template=config_template,
        instance_config=instance_config1,
    ) as (plugin, version, instance):
        # Add this plugin to the list which will be cast into the PromptCompletionPluginInstance class.
        Steamship.register_plugin_shim(plugin.handle, PromptGenerationPluginInstance)

        # Now we just invoke use_plugin.
        # Note: this just applies Steamship.use_plugin with the same testing environment as the unit tests.
        llm = steamship_use_plugin(plugin.handle, version=version.handle)

        # And we can run a prompt
        result = llm.generate("This is my prompt", {})

        # The result should be a string equal to the preset string of this (fake) prompt completion plugin
        assert fixed_prompt_response == result
