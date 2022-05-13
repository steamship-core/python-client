from steamship.extension.file import File

__copyright__ = "Steamship"
__license__ = "MIT"

from tests import APPS_PATH
from tests.utils.client import get_steamship_client
from tests.utils.deployables import deploy_plugin


def test_e2e_blockifier_plugin():
    client = get_steamship_client()
    blockifier_path = APPS_PATH / "plugins" / "blockifiers" / "blockifier.py"
    with deploy_plugin(client, blockifier_path, "blockifier") as (
        plugin,
        version,
        instance,
    ):
        file = File.create(client=client, content="This is a test.").data
        assert len(file.refresh().data.blocks) == 0
        file.blockify(plugin_instance=instance.handle).wait()
        assert len(file.refresh().data.blocks) == 4
        file.delete()
