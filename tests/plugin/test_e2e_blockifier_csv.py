from .. import APPS_PATH

__copyright__ = "Steamship"
__license__ = "MIT"

from ..utils.client import get_steamship_client

from ..utils.file import upload_file
from ..utils.plugin import deploy_plugin


def test_e2e_csv_blockifier_plugin():
    csv_blockifier_plugin_path = APPS_PATH / "plugin_blockifier_csv.py"
    client = get_steamship_client()

    version_config_template = dict(
        textColumn=dict(type="string"),
        tagColumns=dict(type="string"),
        tagKind=dict(type="string"),
    )
    instance_config = dict(
        textColumn="Message", tagColumns="Category", tagKind="Intent"
    )
    with deploy_plugin(
        client,
        csv_blockifier_plugin_path,
        "blockifier",
        version_config_template=version_config_template,
        instance_config=instance_config,
    ) as (plugin, version, instance):
        with upload_file(client, "utterances.csv") as file:
            assert len(file.query().data.blocks) == 0
            file.blockify(pluginInstance=instance.handle).wait()
            assert len(file.query().data.blocks) == 5
            file.delete()
