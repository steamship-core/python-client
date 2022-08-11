from typing import cast

from assets.plugins.blockifiers.async_blockifier import ASYNC_JOB_ID, STATUS_MESSAGE
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.file import upload_file
from steamship_tests.utils.fixtures import get_steamship_client

from steamship.base import Response
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput


def test_e2e_async_blockifier_plugin():
    async_blockifier_plugin_path = PLUGINS_PATH / "blockifiers" / "async_blockifier.py"
    client = get_steamship_client()

    version_config_template = {
        "text_column": {"type": "string"},
        "tag_columns": {"type": "string"},
        "tag_kind": {"type": "string"},
    }
    instance_config = {"text_column": "Message", "tag_columns": "Category", "tag_kind": "Intent"}

    with deploy_plugin(
        client,
        async_blockifier_plugin_path,
        "blockifier",
        version_config_template=version_config_template,
        instance_config=instance_config,
    ) as (plugin, version, instance):
        with upload_file(client, "utterances.csv") as file:
            assert len(file.refresh().data.blocks) == 0
            blockify_response = cast(
                Response[BlockAndTagPluginOutput], file.blockify(plugin_instance=instance.handle)
            )
            blockify_response.wait()

            # Check that the response has the correct bits set indicating that the engine handled it as an async
            # external task.
            assert blockify_response.task.remote_status_input
            assert blockify_response.task.remote_status_input.get("async_job_id") == ASYNC_JOB_ID
            assert blockify_response.task.remote_status_message == STATUS_MESSAGE
            assert blockify_response.task.retries
            assert blockify_response.task.retries == 1

            # Check the number of blocks
            blocks = file.refresh().data.blocks
            assert len(blocks) == 5
            # Check if the tags are correctly added
            for block in blocks:
                assert block.tags is not None
                assert len(block.tags) > 0
                for tag in block.tags:
                    assert tag.name is not None
                    assert tag.kind is not None
            file.delete()
