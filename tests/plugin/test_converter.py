from steamship.plugin.converter import ConvertRequest
from steamship.plugin.service import PluginRequest

from ..demo_apps.plugin_converter import TestConverterPlugin

__copyright__ = "Steamship"
__license__ = "MIT"


def test_resp():
    converter = TestConverterPlugin()
    request = PluginRequest(data=ConvertRequest(data="Hi there"))
    response = converter.run(request).data
    assert (response.file is not None)
    assert (len(response.file.blocks) == 5)

    # Now test as an HTTP Call
