from steamship import File, PluginInstance

from ..client.helpers import deploy_plugin, _steamship, _random_corpus
from ..demo_apps.plugin_file_importer import TEST_DOC

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_corpus_importer():
    client = _steamship()
    test_file_importer_instance = PluginInstance.create(
        client, plugin_handle="test-fileImporter-valueOrData", upsert=True
    ).data
    with deploy_plugin("plugin_corpus_importer.py", "corpusImporter") as (
        plugin,
        version,
        instance,
    ):
        # with PluginVersion.(client, "corpusImporter", "do_import", app, instance) as plugin:
        with _random_corpus(client) as corpus:
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
