from assets.plugins.taggers.plugin_trainable_tagger import (
    TRAINING_PARAMETERS,
    TestTrainableTaggerPlugin,
    make_train_response,
)
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import File
from steamship.base import Task
from steamship.data.block import Block
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.request import PluginRequestContext

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
TEST_PLUGIN_REQ = PluginRequest(
    data=TEST_REQ, context=PluginRequestContext(plugin_instance_id="000")
)
TEST_PLUGIN_REQ_DICT = TEST_PLUGIN_REQ.dict(by_alias=True)


def _test_resp(res):
    pass
    # assert len(res.data.file.tags) == 3
    # TODO: Finish writing steamship_tests in a future PR once the general design of this is finished.


def test_trainable_tagger():
    client = get_steamship_client()
    assert client is not None

    plugin = TestTrainableTaggerPlugin(client=client)
    assert plugin.client is not None

    # STEP 1. Training Parameters
    # The first part of trainable is to produce trainable parameters. The end-user may offer inputs to this,
    # but ultimately it is the plugin itself which decides upon the final set of trainable parameters.
    tagger1 = plugin.get_training_parameters(
        PluginRequest(
            data=TrainingParameterPluginInput(),
            status=Task(task_id="000"),
            context=PluginRequestContext(plugin_instance_id="000"),
        )
    )
    assert tagger1.data.dict() == TRAINING_PARAMETERS.dict()
    tagger2 = plugin.get_training_parameters_endpoint(
        **PluginRequest(
            data=TrainingParameterPluginInput(),
            status=Task(task_id="000"),
            context=PluginRequestContext(plugin_instance_id="000"),
        ).dict()
    )
    assert tagger2.data.dict() == TRAINING_PARAMETERS.dict()
    assert tagger2.data.training_epochs == TRAINING_PARAMETERS.training_epochs

    # STEP 2. Training
    # The first part of trainable is to produce your own trainable parameters.
    model = plugin.model_cls()()
    tagger1 = plugin.train(
        PluginRequest(
            data=TrainPluginInput(
                plugin_instance="foo", training_params=TRAINING_PARAMETERS.training_params
            ),
            status=Task(task_id="000"),
            context=PluginRequestContext(plugin_instance_id="000"),
        ),
        model,
    )
    train_response = make_train_response()
    train_response.data.archive_path = "000/default.zip"
    train_response.data = train_response.data.dict(by_alias=True)
    assert tagger1.data == train_response.data

    tagger2 = plugin.train_endpoint(
        **PluginRequest(
            data=TrainPluginInput(
                plugin_instance="foo", training_params=TRAINING_PARAMETERS.training_params
            ),
            status=Task(task_id="000"),
            context=PluginRequestContext(plugin_instance_id="000"),
        ).dict()
    )

    assert tagger2.data == train_response.data

    # STEP 3. Run
    res = plugin.run(TEST_PLUGIN_REQ)
    _test_resp(res)

    # The endpoints take a kwargs block which is transformed into the appropriate JSON object
    res2 = plugin.run_endpoint(**TEST_PLUGIN_REQ_DICT)
    _test_resp(res2)
