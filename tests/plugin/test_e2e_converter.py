from steamship import BlockTypes, File

from ..client.helpers import deploy_plugin, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_converter():
    client = _steamship()
    with deploy_plugin("plugin_converter.py", "converter") as (plugin, version, instance):
        file = File.upload(client=client, name="Test.txt", content="This is a test.").data
        assert (len(file.query(blockType=BlockTypes.H1).data.blocks) == 0)

        # Use the plugin we just registered
        file.convert(pluginInstance=instance.handle).wait()
        headers = file.query(blockType=BlockTypes.H1).data
        assert (len(file.query(blockType=BlockTypes.H1).data.blocks) == 1)
        assert (len(file.query(blockType=BlockTypes.Paragraph).data.blocks) == 2)

        file.delete()
