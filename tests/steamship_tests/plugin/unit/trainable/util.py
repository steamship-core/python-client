from steamship_tests.base.test_task import NoOpResult

from steamship.base.response import Response
from steamship.base.tasks import TaskState

PLUGIN_INSTANCE_ID = "0000-0000-0000-0000"


def create_dummy_training_task(client) -> Response[NoOpResult]:
    # Create a task that is running in the background
    result = client.post("task/noop", expect=NoOpResult, as_background_task=True)
    assert result.task is not None
    assert result.task.state == TaskState.waiting

    # Allow it to complete
    result.wait()
    assert result.task.state == TaskState.succeeded

    return result
