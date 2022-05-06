from dataclasses import asdict

from steamship.data.plugin_instance import PluginInstance
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from .. import APPS_PATH

__copyright__ = "Steamship"
__license__ = "MIT"

from ..utils.client import get_steamship_client
from ..utils.file import upload_file
from ..utils.plugin import deploy_plugin

EXPORTER_HANDLE = "signed-url-exporter"


def test_e2e_corpus_export():
    client = get_steamship_client()
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
    exporterPluginR = PluginInstance.create(
        client=client,
        handle=EXPORTER_HANDLE,
        pluginHandle=EXPORTER_HANDLE,
        upsert=True
    )
    assert (exporterPluginR.data is not None)
    exporterPlugin = exporterPluginR.data
    assert (exporterPlugin.handle is not None)

    input = ExportPluginInput(handle='default', type="corpus")
    print(asdict(input))

    csv_blockifier_path = APPS_PATH / "plugins" / "csv_blockifier.py"

    # Make a blockifier which will generate our training corpus
    with deploy_plugin(client, csv_blockifier_path, "blockifier", version_config_template=versionConfigTemplate,
                       instance_config=instanceConfig) as (plugin, version, instance):
        with upload_file(client, "utterances.csv") as file:
            assert (len(file.query().data.blocks) == 0)
            # Use the plugin we just registered
            file.blockify(pluginInstance=instance.handle).wait()
            assert (len(file.query().data.blocks) == 5)

            # Now export the corpus
            rawDataR = exporterPlugin.export(input)
            assert (rawDataR is not None)

            # The results of a corpus exporter are MD5 encoded!
            rawData = rawDataR.data
