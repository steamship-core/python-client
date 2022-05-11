import base64
import json
from dataclasses import asdict

import requests

from steamship.data import Block, Tag
from steamship.data.plugin_instance import PluginInstance
from steamship.extension.file import File
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput

from .. import APPS_PATH

__copyright__ = "Steamship"
__license__ = "MIT"

from ..utils.client import get_steamship_client
from ..utils.deployables import deploy_plugin
from ..utils.file import upload_file

EXPORTER_HANDLE = "signed-url-exporter"


def test_e2e_corpus_export():
    client = get_steamship_client()
    version_config_template = dict(
        text_column=dict(type="string"),
        tag_columns=dict(type="string"),
        tag_kind=dict(type="string"),
    )  # TODO (enias): Derive this from Config
    instance_config = dict(  # Has to match up
        text_column="Message",
        tag_columns="Category",
        tag_kind="Intent",
    )
    exporter_plugin_r = PluginInstance.create(
        client=client,
        handle=EXPORTER_HANDLE,
        plugin_handle=EXPORTER_HANDLE,
        upsert=True,
    )
    assert exporter_plugin_r.data is not None
    exporter_plugin = exporter_plugin_r.data
    assert exporter_plugin.handle is not None

    _input = ExportPluginInput(handle="default", type="corpus")
    print(asdict(_input))

    csv_blockifier_path = APPS_PATH / "plugins" / "blockifiers" / "csv_blockifier.py"

    # Make a blockifier which will generate our training corpus
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


def test_e2e_corpus_export_with_query():
    client = get_steamship_client()
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
    print(asdict(_input))
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
    files = [File.from_dict(json.loads(line)) for line in content.splitlines()]
    assert len(files) == 1
    assert len(files[0].tags) == 1

    a.delete()
    b.delete()
