import base64

from assets.plugins.importers.plugin_file_importer import TEST_DOC, TestFileImporterPlugin

from steamship.data.file import File
from steamship.invocable import InvocableResponse
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput

TEST_REQ = File.CreateRequest()
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_PLUGIN_REQ_DICT = TEST_PLUGIN_REQ.dict()


def _test_resp(res):
    assert isinstance(res, InvocableResponse)
    assert isinstance(res.data, RawDataPluginOutput)
    b64 = base64.b64encode(TEST_DOC.encode("utf-8")).decode("utf-8")
    assert res.data.data == b64


def test_importer():
    importer = TestFileImporterPlugin()
    res = importer.run(TEST_PLUGIN_REQ)
    _test_resp(res)

    # The endpoints take a kwargs block which is transformed into the appropriate JSON object
    res2 = importer.run_endpoint(**TEST_PLUGIN_REQ_DICT)
    _test_resp(res2)
