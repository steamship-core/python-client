import json

from steamship import SteamshipError

__copyright__ = "Steamship"
__license__ = "MIT"

from steamship.base.tasks import TaskState
from tests.utils.client import get_steamship_client
from tests.base.test_task import NoOpResult
from steamship.base.training_task_updater import TrainingTaskUpdater


def test_training_progress_wrapper():
    client = get_steamship_client()

    # Create a task that is running in the background
    result_2 = client.post(
        "task/noop",
        expect=NoOpResult,
        as_background_task=True
    )
    assert (result_2.task is not None)
    assert (result_2.task.state == TaskState.waiting)

    # Allow it to complete
    result_2.wait()
    assert (result_2.task.state == TaskState.succeeded)

    # Let's experiment with some calls

    # Call 1: Fail
    updater = TrainingTaskUpdater(result_2.task)

    error = SteamshipError(message="Oh no!")
    updater.record_training_failed(error=error)

    result_2.check()
    assert (result_2.task.state == TaskState.failed)
    assert (result_2.task.output == json.dumps(error.to_dict()))

    # Call 2: Succeed
    output_dict = {"meaning_of_life": 42}
    updater.record_training_complete(output_dict=output_dict)

    result_2.check()
    assert (result_2.task.state == TaskState.succeeded)
    assert (result_2.task.output == json.dumps(output_dict))

    # Call 3: Update
    output_dict_2 = {"meaning_of_life": "uncertain"}
    updater.record_training_progress(progress_dict=output_dict_2)

    result_2.check()
    assert (result_2.task.state == TaskState.succeeded)
    assert (result_2.task.output == json.dumps(output_dict_2))
