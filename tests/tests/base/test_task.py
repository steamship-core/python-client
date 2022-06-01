from __future__ import annotations

from pydantic import BaseModel

from steamship.base.tasks import TaskState
from tests.utils.fixtures import get_steamship_client


class NoOpResult(BaseModel):
    pass


def test_background_task_call():
    client = get_steamship_client()

    # The No-Op API call literally does nothing.
    result_1 = client.post(
        "task/noop",
        expect=NoOpResult,
    )
    assert result_1.task is None
    assert result_1.data is not None
    assert type(result_1.data) == NoOpResult

    # When we background it, we get a task back instead
    result_2 = client.post("task/noop", expect=NoOpResult, as_background_task=True)
    assert result_2.task is not None
    assert result_2.task.state == TaskState.waiting

    result_2.wait()

    # And now it has completed
    assert result_2.task.state == TaskState.succeeded
    assert result_2.data is not None
    assert type(result_1.data) == NoOpResult


def test_task_update():
    client = get_steamship_client()

    # We'll background this operation in order to transform it into a task we can manipulate
    result_2 = client.post("task/noop", expect=NoOpResult, as_background_task=True)
    assert result_2.task is not None
    assert result_2.task.state == TaskState.waiting

    result_2.wait()

    assert result_2.task.state == TaskState.succeeded

    # Now we've got a task that the Engine is done with. Let's test that we are permitted to manipulate it.
    # TODO(ted): Right now only a user can update their own tasks. We should limit the scope even further so that
    # a user can update their own tasks in a constrained, workflow-compatible way.

    ORIG_INPUT = result_2.task.input
    ORIG_STATUS = result_2.task.status_message

    INPUT = '{"test": "input"}'
    STATUS = "Status Message"

    result_2.task.input = INPUT
    result_2.task.status_message = STATUS

    # Only update the output field.
    result_2.task.post_update(
        fields={
            "status_message",
        }
    )

    # This will refresh the task.
    result_2.refresh()

    # The original input is unchanged; the local modifications have been overwritten by the remote state, which
    # was not updated.
    assert result_2.task.input == ORIG_INPUT

    # The output is the new output. The remote state was updated by the client before the refresh returned
    assert result_2.task.status_message == STATUS
    assert result_2.task.status_message != ORIG_STATUS
