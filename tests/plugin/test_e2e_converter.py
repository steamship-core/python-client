from steamship import App, AppVersion, AppInstance

from ..client.helpers import deploy_app, register_app_as_plugin, _steamship, create_app_zip
from steamship import BlockTypes, File

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_converter():
    client = _steamship()
    with deploy_app("plugin_converter.py") as (app, version, instance):
        with register_app_as_plugin(client, "converter", "convert", app, instance) as plugin:

            file = File.upload(client=client, name="Test.txt", content="This is a test.").data
            assert (len(file.query(blockType=BlockTypes.H1).data.blocks) == 0)

            # Use the plugin we just registered
            file.convert(model=plugin.handle).wait()
            headers = file.query(blockType=BlockTypes.H1).data
            assert (len(file.query(blockType=BlockTypes.H1).data.blocks) == 1)
            assert (len(file.query(blockType=BlockTypes.Paragraph).data.blocks) == 2)

            file.delete()
