import logging

from assets.plugins.taggers.plugin_third_party_trainable_tagger import MockClient
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.client import get_steamship_client
from steamship_tests.utils.deployables import deploy_plugin

from steamship.base import TaskState
from steamship.data.plugin import HostingType
from steamship.data.plugin_instance import PluginInstance
from steamship.data.space import Space
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput

EXPORTER_HANDLE = "signed-url-exporter"


def test_e2e_third_party_trainable_tagger_lambda_training():
    client = get_steamship_client()
    space_r = Space.get(client)  # TODO (enias): Remove
    assert space_r.data is not None

    exporter_plugin_r = PluginInstance.create(
        client=client,
        handle=EXPORTER_HANDLE,
        plugin_handle=EXPORTER_HANDLE,
        upsert=True,  # Don't care if it already exists
    )
    assert exporter_plugin_r.data is not None
    exporter_plugin = exporter_plugin_r.data
    assert exporter_plugin.handle is not None

    third_party_trainable_tagger_path = (
        PLUGINS_PATH / "taggers" / "plugin_third_party_trainable_tagger.py"
    )

    # Note that we're going to do the below training on ZERO data for simplicity.
    # The particular test model doesn't actually incorporate any data given to it at training time, so
    # it would just slow the test down to create, blockify, and export a training corpus.

    with deploy_plugin(
        client, third_party_trainable_tagger_path, "tagger", training_platform=HostingType.LAMBDA
    ) as (tagger, tagger_version, tagger_instance):
        # Now train the plugin
        training_request = TrainingParameterPluginInput(
            plugin_instance=tagger_instance.handle,
            export_plugin_input=ExportPluginInput(
                plugin_instance=exporter_plugin.handle, type="file", query="all"
            ),
        )
        train_result = tagger_instance.train(training_request)
        train_result.wait()
        assert train_result.task.state is not TaskState.failed
        assert train_result.task.remote_status_input is not None
        assert train_result.task.remote_status_input["num_checkins"] == 2

        assert train_result.data is not None

        logging.info("Waiting 15 seconds for instance to deploy.")
        import time

        time.sleep(15)

        # Now we'll attempt to USE this plugin. This plugin's behavior is to simply tag every block with
        # the parameters `MockClient.LABELS`

        # First we'll create a file
        test_doc = "Hi there"
        res = tagger_instance.tag(doc=test_doc)
        res.wait()
        assert res.error is None
        assert res.data is not None
        assert res.data.file is not None
        assert not res.data.file.tags
        assert res.data.file.blocks is not None
        assert len(res.data.file.blocks) > 0
        for block in res.data.file.blocks:
            assert block.tags is not None
            assert sorted([tag.name for tag in block.tags]) == sorted(MockClient.LABELS)
