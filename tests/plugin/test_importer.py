from steamship.app import Response
from steamship.data.file import File
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput
from steamship.plugin.service import PluginRequest

__copyright__ = "Steamship"
__license__ = "MIT"

import base64

from tests.demo_apps.plugins.importers.plugin_file_importer import TEST_DOC, TestFileImporterPlugin

TEST_REQ = File.CreateRequest(value="Hi there.")
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def _test_resp(res):
    assert type(res) == Response
    assert type(res.data) == RawDataPluginOutput
    b64 = base64.b64encode(TEST_DOC.encode("utf-8")).decode("utf-8")
    assert res.data.data == b64


def test_importer():
    importer = TestFileImporterPlugin()
    res = importer.run(TEST_PLUGIN_REQ)
    _test_resp(res)
