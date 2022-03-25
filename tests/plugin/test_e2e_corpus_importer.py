from steamship import File, Corpus, Plugin, PluginVersion, PluginInstance

from ..client.helpers import deploy_plugin, _steamship, _random_corpus
from ..demo_apps.plugin_file_importer import TEST_DOC

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_corpus_importer():
    client = _steamship()
    fileImporterPlugin = Plugin.getPublic(client, handle='test-fileImporter-valueOrData')
    fileImporterPluginVersion = PluginVersion.getPublic(client, pluginId=fileImporterPlugin.id, handle='1.0')
    testFileImporterInstance = PluginInstance.create(client, fileImporterPlugin.id, fileImporterPluginVersion.id, handle='testFileImporter', upsert=True).data
    with deploy_plugin("plugin_corpus_importer.py", "corpusImporter") as (plugin, version, instance):
        #with PluginVersion.(client, "corpusImporter", "do_import", app, instance) as plugin:
        with _random_corpus(client) as corpus:
            resp = corpus.doImport(
                pluginInstance=instance.handle,
                fileImporterPluginInstance=testFileImporterInstance.handle,
                value="dummy-value"
            )
            resp.wait()

            # We should now have two files!
            files = File.list(client, corpusId=corpus.id).data
            assert (files.files is not None)
            assert (len(files.files) == 2)

            for file in files.files:
                data = file.raw().data
                assert (data.decode('utf-8') == TEST_DOC)
                file.delete()
