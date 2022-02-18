from steamship import File, Corpus

from ..client.helpers import deploy_app, register_app_as_plugin, _steamship, _random_corpus
from ..demo_apps.plugin_file_importer import TEST_DOC

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_corpus_importer():
    client = _steamship()
    with deploy_app("plugin_corpus_importer.py") as (app, version, instance):
        with register_app_as_plugin(client, "corpusImporter", "do_import", app, instance) as plugin:
            with _random_corpus(client) as corpus:
                resp = corpus.doImport(
                    plugin=plugin.handle,
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
