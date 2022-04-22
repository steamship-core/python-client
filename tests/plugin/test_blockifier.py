from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.service import PluginRequest

from ..demo_apps.plugin_blockifier import TestBlockifierPlugin

__copyright__ = "Steamship"
__license__ = "MIT"


def test_resp():
    blockifier = TestBlockifierPlugin()
    request = PluginRequest(data=RawDataPluginInput(data="Hi there"))
    response = blockifier.run(request).data
    assert (response.file is not None)
    assert (len(response.file.blocks) == 4)

    # Now test as an HTTP Call
