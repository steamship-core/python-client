from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import File


def test_e2e_blockifier_plugin():
    client = get_steamship_client()
    blockifier_path = PLUGINS_PATH / "blockifiers" / "blockifier_with_secrets.py"
    with deploy_plugin(client, blockifier_path, "blockifier", secrets_toml='secret="FOO"') as (
        plugin,
        version,
        instance,
    ):
        file = File.create(client=client, content="This is a test.")
        assert len(file.refresh().blocks) == 0
        file.blockify(plugin_instance=instance.handle).wait()
        file.refresh()
        assert len(file.blocks) == 1
        assert file.blocks[0].text == "FOO"
        file.delete()
