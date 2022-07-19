import base64
import json

import pytest
import requests
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.file import upload_file

from steamship import File
from steamship.client import Steamship
from steamship.data import Block, Tag
from steamship.data.plugin_instance import PluginInstance
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput

EXPORTER_HANDLE = "signed-url-exporter"


@pytest.mark.usefixtures("client")
def test_e2e_corpus_export(client: Steamship):
    version_config_template = {
        "text_column": {"type": "string"},
        "tag_columns": {"type": "string"},
        "tag_kind": {"type": "string"},
    }  # TODO (enias): Derive this from Config
    instance_config = {  # Has to match up
        "text_column": "Message",
        "tag_columns": "Category",
        "tag_kind": "Intent",
    }
    exporter_plugin_r = PluginInstance.create(
        client=client,
        handle=EXPORTER_HANDLE,
        plugin_handle=EXPORTER_HANDLE,
        upsert=True,
    )
    assert exporter_plugin_r.data is not None
    exporter_plugin = exporter_plugin_r.data
    assert exporter_plugin.handle is not None

    _input = ExportPluginInput(handle="default", type="file")

    csv_blockifier_path = PLUGINS_PATH / "blockifiers" / "csv_blockifier.py"

    # Make a blockifier which will generate our trainable corpus
    with deploy_plugin(
        client,
        csv_blockifier_path,
        "blockifier",
        version_config_template=version_config_template,
        instance_config=instance_config,
    ) as (plugin, version, instance):
        with upload_file(client, "utterances.csv") as file:
            assert len(file.refresh().data.blocks) == 0
            # Use the plugin we just registered
            file.blockify(plugin_instance=instance.handle).wait()
            assert len(file.refresh().data.blocks) == 5

            # Now export the corpus
            raw_data_r = exporter_plugin.export(_input)
            assert raw_data_r is not None

            # The results of a corpus exporter are MD5 encoded!
            _ = raw_data_r.data


def test_e2e_corpus_export_with_query(client):
    exporter_plugin_r = PluginInstance.create(
        client=client,
        handle=EXPORTER_HANDLE,
        plugin_handle=EXPORTER_HANDLE,
        upsert=True,
    )
    assert exporter_plugin_r.data is not None
    exporter_plugin = exporter_plugin_r.data
    assert exporter_plugin.handle is not None

    a = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A", tags=[Tag.CreateRequest(name="BlockTag")]),
            Block.CreateRequest(text="B"),
        ],
    ).data
    assert a.id is not None
    b = File.create(
        client=client,
        blocks=[Block.CreateRequest(text="A"), Block.CreateRequest(text="B")],
        tags=[Tag.CreateRequest(name="FileTag")],
    ).data
    assert b.id is not None

    # Now export the corpus
    _input = ExportPluginInput(query='filetag and name "FileTag"', type="file")
    raw_data_r = exporter_plugin.export(_input)
    assert raw_data_r is not None

    # The results of a corpus exporter are MD5 encoded!
    raw_data_r.wait()
    raw_data = raw_data_r.data.data
    # decode base64 to get URL at url json property
    decoded_data = json.loads(base64.b64decode(raw_data))
    url = decoded_data["url"]

    # fetch the URL via requests.get
    content = requests.get(url).text

    # Look at lines of jsonl file
    files = [File.parse_obj(json.loads(line)) for line in content.splitlines()]
    assert len(files) == 1
    assert len(files[0].tags) == 1

    a.delete()
    b.delete()
