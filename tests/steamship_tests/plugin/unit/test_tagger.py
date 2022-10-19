import pytest
from assets.plugins.taggers.plugin_parser import TestParserPlugin

from steamship import File
from steamship.data.block import Block
from steamship.invocable import InvocableResponse
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput

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
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_PLUGIN_REQ_DICT = TEST_PLUGIN_REQ.dict()


def _test_resp(res):
    assert isinstance(res, InvocableResponse)
    assert isinstance(res.data, BlockAndTagPluginOutput)
    assert len(res.data.file.blocks) == 1
    assert res.data.file.blocks[0].text == TEST_REQ.file.blocks[0].text
    assert len(res.data.file.blocks[0].tags) == 3


def test_parser():
    parser = TestParserPlugin()
    res = parser.run(TEST_PLUGIN_REQ)
    _test_resp(res)

    # The endpoints take a kwargs block which is transformed into the appropriate JSON object
    res2 = parser.run_endpoint(**TEST_PLUGIN_REQ_DICT)
    _test_resp(res2)

    # This plugin is not trainable, and thus it refuses trainable parameters requests
    with pytest.raises(AttributeError):
        parser.get_training_parameters(PluginRequest(data=TrainingParameterPluginInput()))
    with pytest.raises(AttributeError):
        parser.get_training_parameters_endpoint(
            **PluginRequest(data=TrainingParameterPluginInput()).dict()
        )

    # This plugin is not trainable, and thus it refuses train requests
    with pytest.raises(AttributeError):
        parser.train(PluginRequest(data=TrainPluginInput()))
    with pytest.raises(AttributeError):
        parser.train_endpoint(**PluginRequest(data=TrainPluginInput()).dict())
