from steamship.extension.file import File

__copyright__ = "Steamship"
__license__ = "MIT"

from tests import APPS_PATH
from tests.utils.client import get_steamship_client
from tests.utils.plugin import deploy_plugin


def test_e2e_blockifier_plugin():
    client = get_steamship_client()
    blockifier_plugin_path = APPS_PATH / "blockifier.py"
    with deploy_plugin(client, blockifier_plugin_path, "blockifier") as (
        plugin,
        version,
        instance,
    ):
        file = File.create(client=client, content="This is a test.").data
        assert len(file.query().data.blocks) == 0
        file.blockify(pluginInstance=instance.handle).wait()
        assert len(file.query().data.blocks) == 4
        file.delete()
