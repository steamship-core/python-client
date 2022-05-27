from assets.plugins.taggers.plugin_trainable_tagger_config import (
    TRAIN_RESPONSE,
    TestTrainableTaggerConfigPlugin,
)

from steamship import File
from steamship.data.block import Block
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.service import PluginRequest
from tests.utils.fixtures import get_steamship_client

TEST_REQ = BlockAndTagPluginInput(
    file=File(
        blocks=[
            Block(
                id="ABC",
                text="Once upon a time there was a magical ship. "
                "The ship was powered by STEAM. The ship went to the moon.",
            )
        ]
    )
)
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ, plugin_instance_id="000")
TEST_PLUGIN_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def test_trainable_tagger():
    client = get_steamship_client()
    assert client is not None

    plugin = TestTrainableTaggerConfigPlugin(
        client=client, config=dict(testValue1="foo", testValue2="bar")
    )
    assert plugin.client is not None

    # Make sure plugin model gets its config while 'training'.

    tagger2 = plugin.train_endpoint(
        **PluginRequest(
            data=TrainPluginInput(plugin_instance="foo", training_params=None),
            task_id="000",
            plugin_instance_id="000",
        ).to_dict()
    )

    # Make sure plugin model gets its config while 'running'
    res = plugin.run(TEST_PLUGIN_REQ)
