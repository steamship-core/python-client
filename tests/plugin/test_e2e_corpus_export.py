from dataclasses import asdict

import requests

from steamship.data.plugin_instance import PluginInstance
from steamship.data.plugin import TrainingPlatform
from steamship.data import Block, Tag
from steamship.extension.file import File
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
import time
import base64
import json

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


def test_e2e_corpus_export_with_query():
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

    a = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A", tags=[Tag.CreateRequest(name="BlockTag")]),
            Block.CreateRequest(text="B")
        ]
    ).data
    assert (a.id is not None)
    b = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A"),
            Block.CreateRequest(text="B")
        ],
        tags=[
            Tag.CreateRequest(name="FileTag")
        ]
    ).data
    assert (b.id is not None)

    # Now export the corpus
    input = ExportPluginInput(query="filetag", type='file')
    print(asdict(input))
    rawDataR = exporterPlugin.export(input)
    assert (rawDataR is not None)

    # The results of a corpus exporter are MD5 encoded!
    rawDataR.wait()
    rawData = rawDataR.data.data
    # decode base64 to get URL at url json property
    decodedData = json.loads(base64.b64decode(rawData))
    url = decodedData['url']


    #fetch the URL via requests.get
    content = requests.get(url).text

    #Look at lines of jsonl file
    files = [File.from_dict(json.loads(line)) for line in content.splitlines()]
    assert(len(files) == 1)
    assert(len(files[0].tags) == 1)

    a.delete()
    b.delete()