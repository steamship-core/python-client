from __future__ import annotations

from steamship_tests.utils.fixtures import get_steamship_client

from steamship.base.model import CamelModel
from steamship.base.tasks import TaskState


class NoOpResult(CamelModel):
    pass


def test_background_task_call():
    client = get_steamship_client()

    # The No-Op API call literally does nothing.
    result_task_1 = client.post(
        "task/noop",
        expect=NoOpResult,
    )
    assert result_task_1 is not None
    assert type(result_task_1) == NoOpResult

    # When we background it, we get a task back instead
    result_2_task = client.post("task/noop", expect=NoOpResult, as_background_task=True)
    assert result_2_task is not None
    assert result_2_task.state == TaskState.waiting

    result_2_task.wait()

    # And now it has completed
    assert result_2_task.state == TaskState.succeeded
    assert result_2_task.output is not None
    assert type(result_2_task.output) == NoOpResult


def test_task_update():
    client = get_steamship_client()

    # We'll background this operation in order to transform it into a task we can manipulate
    result_task = client.post("task/noop", expect=NoOpResult, as_background_task=True)
    assert result_task is not None
    assert result_task.state == TaskState.waiting

    result_task.wait()

    assert result_task.state == TaskState.succeeded

    # Now we've got a task that the Engine is done with. Let's test that we are permitted to manipulate it.
    # TODO(ted): Right now only a user can update their own tasks. We should limit the scope even further so that
    # a user can update their own tasks in a constrained, workflow-compatible way.

    orig_input = result_task.input
    orig_status = result_task.status_message

    input = '{"test": "input"}'
    status = "Status Message"

    result_task.input = input
    result_task.status_message = status

    # Only update the output field.
    result_task.post_update(
        fields={
            "status_message",
        }
    )

    # This will refresh the task.
    result_task.refresh()

    # The original input is unchanged; the local modifications have been overwritten by the remote state, which
    # was not updated.
    assert result_task.input == orig_input

    # The output is the new output. The remote state was updated by the client before the refresh returned
    assert result_task.status_message == status
    assert result_task.status_message != orig_status
