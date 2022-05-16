import json

from steamship import SteamshipError

__copyright__ = "Steamship"
__license__ = "MIT"

from steamship.base.tasks import TaskState
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.trainable.model_loader import ModelLoader
from tests.utils.client import get_steamship_client
from tests.base.test_task import NoOpResult
from steamship.plugin.trainable.model_trainer import ModelTrainer


def test_trainer_status_updates():
    client = get_steamship_client()

    # Create a task that is running in the background
    result_2 = client.post("task/noop", expect=NoOpResult, as_background_task=True)
    assert result_2.task is not None
    assert result_2.task.state == TaskState.waiting

    # Allow it to complete
    result_2.wait()
    assert result_2.task.state == TaskState.succeeded

    # Let's experiment with some calls. We'll start a trainer with a dummy plugin instance ID
    # and pass it the task ID to update to.
    PLUGIN_INSTANCE_ID = "0000-0000-0000-0000"
    TASK_ID = result_2.task.task_id
    TRAIN_PLUGIN_INPUT = TrainPluginInput(trainTaskId=TASK_ID)

    trainer = ModelTrainer(
        client=client,
        plugin_instance_id=PLUGIN_INSTANCE_ID,
        train_plugin_input=TrainPluginInput(trainTaskId=TASK_ID)
    )

    # Call 1: Fail
    error = SteamshipError(message="Oh no!")
    trainer.record_training_failed(error=error)

    result_2.check()
    assert result_2.task.state == TaskState.failed
    assert result_2.task.output == json.dumps(error.to_dict())

    # Call 2: Succeed
    output_dict = {"meaning_of_life": 42}
    trainer.record_training_complete(output_dict=output_dict)

    result_2.check()
    assert result_2.task.state == TaskState.succeeded
    assert result_2.task.output == json.dumps(output_dict)

    # Call 3: Update
    output_dict_2 = {"meaning_of_life": "uncertain"}
    trainer.record_training_progress(progress_dict=output_dict_2)

    result_2.check()
    assert result_2.task.state == TaskState.succeeded
    assert result_2.task.output == json.dumps(output_dict_2)
