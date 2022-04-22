from steamship import DocTag
from steamship.extension.file import File

from ..client.helpers import deploy_plugin, upload_file, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_blockifier():
    client = _steamship()
    versionConfigTemplate = dict(
        textColumn=dict(type="string"),
        tagColumns=dict(type="string"),
        tagKind=dict(type="string")
    )
    instanceConfig = dict(
        textColumn="Message",
        tagColumns="Category",
        tagKind="Intent"
    )
    with deploy_plugin("plugin_blockifier_csv.py", "blockifier", versionConfigTemplate=versionConfigTemplate, instanceConfig=instanceConfig) as (plugin, version, instance):
        with upload_file("utterances.csv") as file:
            assert (len(file.query().data.blocks) == 0)

            # Use the plugin we just registered
            file.blockify(pluginInstance=instance.handle).wait()
            assert (len(file.query().data.blocks) == 5)

            file.delete()
