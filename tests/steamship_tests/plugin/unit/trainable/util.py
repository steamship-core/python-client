from steamship_tests.base.test_task import NoOpResult

from steamship.base.tasks import Task, TaskState

PLUGIN_INSTANCE_ID = "0000-0000-0000-0000"


def create_dummy_training_task(client) -> Task[NoOpResult]:
    # Create a task that is running in the background
    task = client.post("task/noop", expect=NoOpResult, as_background_task=True)
    assert task is not None
    assert task.state == TaskState.waiting

    # Allow it to complete
    task.wait()
    assert task.state == TaskState.succeeded

    return task
