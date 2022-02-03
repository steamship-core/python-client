from steamship import SteamshipError, Block
from steamship.plugin.converter import ClientsideConvertRequest, ConvertResponse, Converter
from steamship.plugin.service import PluginRequest, PluginResponse
from ..demo_apps.plugin_converter import TestConverterPlugin

__copyright__ = "Steamship"
__license__ = "MIT"


def test_resp():
    converter = TestConverterPlugin()
    request = PluginRequest(data=ClientsideConvertRequest(data="Hi there"))
    response = converter.run(request).data
    assert(response.root is not None)
    assert(len(response.root.children) == 3)

    # Now test as an HTTP Call