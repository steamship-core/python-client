from steamship import File

from ..client.helpers import deploy_plugin, _steamship
from ..demo_apps.plugin_file_importer import TEST_DOC

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_importer():
    client = _steamship()
    with deploy_plugin("plugin_file_importer.py","fileImporter") as (plugin, version, instance):
        file = File.create(
            client=client,
            name="Test.txt",
            content="This is a test.",
            pluginInstance=instance.handle
        ).data

        data = file.raw().data

        assert (data.decode('utf-8') == TEST_DOC)

        file.delete()
