from tests.base.test_task import NoOpResult

def setup_model_and_checkpoint(client) -> (str, str, ModelCheckpoint):
    # Create a task that is running in the background
    result_2 = client.post(
        "task/noop",
        expect=NoOpResult,
        as_background_task=True
    )
    assert (result_2.task is not None)
    assert (result_2.task.state == TaskState.waiting)
