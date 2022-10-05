from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import File
from steamship.data.operations.corpus_importer import CorpusImportRequest, CorpusImportResponse

HANDLE = "test-importer-plugin-v1"
TEST_H1 = "A Poem"
TEST_S1 = "Roses are red."
TEST_S2 = "Violets are blue."
TEST_S3 = "Sugar is sweet, and I love you."
TEST_DOC = f"# {TEST_H1}\n\n{TEST_S1} {TEST_S2}\n\n{TEST_S3}\n"


def test_e2e_corpus_importer():
    client = get_steamship_client()
    corpus_importer_path = PLUGINS_PATH / "importers" / "plugin_corpus_importer.py"
    file_importer_path = PLUGINS_PATH / "importers" / "plugin_file_importer.py"

    with deploy_plugin(client, file_importer_path, "fileImporter") as (
        _,
        _,
        fi_instance,
    ):
        with deploy_plugin(client, corpus_importer_path, "corpusImporter") as (
            plugin,
            version,
            instance,
        ):
            req = CorpusImportRequest(
                type="file",
                value="dummy-value",
                plugin_instance=instance.handle,
                file_importer_plugin_instance=fi_instance.handle,
            )
            res = client.post(
                "plugin/instance/importCorpus",
                req,
                expect=CorpusImportResponse,
            )
            res.wait()

            # We should now have two files!
            files = File.list(client).data
            assert files.files is not None
            assert len(files.files) == 2

            for file in files.files:
                data = file.raw().data
                assert data.decode("utf-8") == TEST_DOC
                file.delete()
