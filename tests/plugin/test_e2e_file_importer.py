from steamship import File
from tests.demo_apps.plugins.importers.plugin_file_importer import TEST_DOC

from .. import APPS_PATH

__copyright__ = "Steamship"
__license__ = "MIT"

from ..utils.client import get_steamship_client
from ..utils.deployables import deploy_plugin


def test_e2e_importer():
    client = get_steamship_client()
    file_importer_path = APPS_PATH / "plugins" / "importers" / "plugin_file_importer.py"

    with deploy_plugin(client, file_importer_path, "fileImporter") as (
        plugin,
        version,
        instance,
    ):
        file = File.create(
            client=client, content="This is a test.", plugin_instance=instance.handle
        ).data

        data = file.raw().data

        assert data.decode("utf-8") == TEST_DOC

        file.delete()
