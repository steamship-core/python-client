from steamship.app import Response
from steamship.data.file import File
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput
from steamship.plugin.service import PluginRequest

__copyright__ = "Steamship"
__license__ = "MIT"

from ..demo_apps.plugin_file_importer import TestFileImporterPlugin, TEST_DOC
import base64

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
