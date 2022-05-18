from steamship import File, PluginInstance
from tests import APPS_PATH
from tests.demo_apps.plugins.importers.plugin_file_importer import TEST_DOC
from tests.utils.client import get_steamship_client
from tests.utils.deployables import deploy_plugin
from tests.utils.random import random_corpus


def test_e2e_corpus_importer():
    client = get_steamship_client()
    corpus_importer_path = APPS_PATH / "plugins" / "importers" / "plugin_corpus_importer.py"

    test_file_importer_instance = PluginInstance.create(
        client, plugin_handle="test-fileImporter-valueOrData", upsert=True
    ).data
    with deploy_plugin(client, corpus_importer_path, "corpusImporter") as (
        plugin,
        version,
        instance,
    ):
        # with PluginVersion.(client, "corpusImporter", "do_import", app, instance) as plugin:
        with random_corpus(client) as corpus:
            resp = corpus.do_import(
                plugin_instance=instance.handle,
                file_importer_plugin_instance=test_file_importer_instance.handle,
                value="dummy-value",
            )
            resp.wait()

            # We should now have two files!
            files = File.list(client, corpus_id=corpus.id).data
            assert files.files is not None
            assert len(files.files) == 2

            for file in files.files:
                data = file.raw().data
                assert data.decode("utf-8") == TEST_DOC
                file.delete()
