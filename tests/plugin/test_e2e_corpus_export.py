from dataclasses import asdict

from steamship.data.plugin_instance import PluginInstance
from steamship.data.plugin import TrainingPlatform
from steamship.extension.file import File
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
import time

from ..client.helpers import deploy_plugin, upload_file, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

EXPORTER_HANDLE = "signed-url-exporter"

def test_e2e_corpus_export():
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

    # Make a blockifier which will generate our training corpus
    with deploy_plugin("plugin_blockifier_csv.py", "blockifier", versionConfigTemplate=versionConfigTemplate, instanceConfig=instanceConfig) as (plugin, version, instance):
        with upload_file("utterances.csv") as file:
            assert (len(file.refresh().data.blocks) == 0)
            # Use the plugin we just registered
            file.blockify(pluginInstance=instance.handle).wait()
            assert (len(file.refresh().data.blocks) == 5)

            # Now export the corpus
            rawDataR = exporterPlugin.export(input)
            assert (rawDataR is not None)

            # The results of a corpus exporter are MD5 encoded!
            rawData = rawDataR.data
