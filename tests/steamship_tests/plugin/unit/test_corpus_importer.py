from assets.plugins.importers.plugin_corpus_importer import TestCorpusImporterPlugin

from steamship.app import Response
from steamship.data.operations.corpus_importer import CorpusImportRequest, CorpusImportResponse
from steamship.plugin.service import PluginRequest

TEST_REQ = CorpusImportRequest(url="1")
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_PLUGIN_REQ_DICT = TEST_PLUGIN_REQ.dict()


def _test_resp(res):
    assert isinstance(res, Response)
    assert isinstance(res.data, CorpusImportResponse)
    assert res.data.file_import_requests is not None
    assert len(res.data.file_import_requests) == 2


def test_importer():
    importer = TestCorpusImporterPlugin()
    res = importer.run(TEST_PLUGIN_REQ)
    _test_resp(res)

    # The endpoints take a kwargs block which is transformed into the appropriate JSON object
    res2 = importer.run_endpoint(**TEST_PLUGIN_REQ_DICT)
    _test_resp(res2)
