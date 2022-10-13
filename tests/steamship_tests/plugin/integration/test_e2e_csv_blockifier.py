from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.file import upload_file
from steamship_tests.utils.fixtures import get_steamship_client


def test_e2e_csv_blockifier_plugin():
    client = get_steamship_client()
    csv_blockifier_plugin_path = PLUGINS_PATH / "blockifiers" / "csv_blockifier.py"

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
    with deploy_plugin(
        client,
        csv_blockifier_plugin_path,
        "blockifier",
        version_config_template=version_config_template,
        instance_config=instance_config,
    ) as (plugin, version, instance):
        with upload_file(client, "utterances.csv") as file:
            assert len(file.refresh().blocks) == 0
            file.blockify(plugin_instance=instance.handle).wait()
            # Check the number of blocks
            blocks = file.refresh().blocks
            assert len(blocks) == 5
            for block in blocks:
                assert block.tags is not None
                assert len(block.tags) > 0
                for tag in block.tags:
                    assert tag.name is not None
                    assert tag.kind is not None
