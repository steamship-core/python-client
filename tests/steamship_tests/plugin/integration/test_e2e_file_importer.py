import pytest
from assets.plugins.blockifiers.blockifier import TEST_DOC
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin

from steamship import File
from steamship.client import Steamship


@pytest.mark.usefixtures("client")
def test_e2e_importer(client: Steamship):
    file_importer_path = PLUGINS_PATH / "importers" / "plugin_file_importer.py"
    with deploy_plugin(client, file_importer_path, "fileImporter") as (
        plugin,
        version,
        instance,
    ):
        # The test FileImporter should always return a string file with contents TEST_DOC
        file_task = File.create_with_plugin(client=client, plugin_instance=instance.handle)
        file = file_task.wait()

        assert len(file.tags) == 1
        assert file.tags[0].kind == "test-kind"
        assert file.tags[0].name == "test-name"

        # Now fetch the data from Steamship and assert that it is the SAME as the data the FileImporter creates
        data = file.raw()
        assert data.decode("utf-8") == TEST_DOC

        fetched_file = File.get(client, _id=file.id)
        assert len(fetched_file.tags) == 1
        assert fetched_file.tags[0].kind == "test-kind"
        assert fetched_file.tags[0].name == "test-name"

        file.delete()
