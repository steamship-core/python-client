from .. import APPS_PATH

__copyright__ = "Steamship"
__license__ = "MIT"

from ..utils.client import get_steamship_client

from ..utils.file import upload_file
from ..utils.plugin import deploy_plugin


def test_e2e_csv_blockifier_plugin():
    csv_blockifier_plugin_path = APPS_PATH / "plugins" / "csv_blockifier.py"
    client = get_steamship_client()

    version_config_template = dict(
        textColumn=dict(type="string"),
        tagColumns=dict(type="string"),
        tagKind=dict(type="string"),
    )  # TODO (enias): Derive this from Config
    instance_config = dict(  # Has to match up
        textColumn="Message",
        tagColumns="Category",
        tagKind="Intent",
    )
    with deploy_plugin(
        client,
        csv_blockifier_plugin_path,
        "blockifier",
        version_config_template=version_config_template,
        instance_config=instance_config,
    ) as (plugin, version, instance):
        with upload_file(client, "utterances.csv") as file:
            assert len(file.refresh().data.blocks) == 0
            file.blockify(plugin_instance=instance.handle).wait()
            # Check the number of blocks
            blocks = file.refresh().data.blocks
            assert len(blocks) == 5
            for block in blocks:
                assert block.tags is not None
                assert len(block.tags) > 0
                for tag in block.tags:
                    assert tag.name is not None
                    assert tag.kind is not None
            file.delete()
