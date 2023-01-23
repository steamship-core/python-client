import pytest
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.client import register_plugin_instance_subclass, steamship_use_plugin
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import SteamshipError
from steamship.data.plugin.prompt_generation_plugin_instance import PromptGenerationPluginInstance


def test_use_prompt():

    client = get_steamship_client()
    tagger_plugin_path = PLUGINS_PATH / "taggers" / "plugin_prompt_generator.py"

    with deploy_plugin(
        client,
        tagger_plugin_path,
        "tagger",
    ) as (plugin, version, instance):
        # Add this plugin to the list which will be cast into the PromptCompletionPluginInstance class.
        register_plugin_instance_subclass(plugin.handle, PromptGenerationPluginInstance)

        # Now we just invoke use_plugin.
        # Note: this just applies Steamship.use_plugin with the same testing environment as the unit tests.
        with steamship_use_plugin(plugin.handle, delete_workspace=True) as llm:
            # And we can run a prompt. Covering some bases to encode edge cases and their expected behavior.

            # Prompt vars: 1, Provided vars: 1
            assert llm.generate("Hello, {name}!", {"name": "world"}) == "Hello, world!"
            # Prompt vars: 0, Provided vars: 1
            assert llm.generate("Hello, World!", {"name": "world"}) == "Hello, World!"
            # Prompt vars: 1, Provided vars: 0
            with pytest.raises(SteamshipError):
                assert llm.generate("Hello, {name}!") == "Hello, {name}!"
            # Prompt vars: 0, Provided vars: 0
            assert llm.generate("Hello, World!") == "Hello, World!"
