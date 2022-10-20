"""When a Plugin's operation is tied to a task, the plugin can update that task while it is still running,
or asynchronously at any time."""

import pytest
from steamship_tests.plugin.unit.trainable.util import create_dummy_training_task
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import SteamshipError
from steamship.base.tasks import Task, TaskState
from steamship.invocable import InvocableResponse


def test_response_post_update_fails_when_no_task_present():
    client = get_steamship_client()
    response = InvocableResponse()
    with pytest.raises(SteamshipError):
        response.post_update(client)

    # No task_id
    response2 = InvocableResponse(status=Task())
    with pytest.raises(SteamshipError):
        response2.post_update(client)


def test_response_post_update_can_update_task():
    client = get_steamship_client()
    task = create_dummy_training_task(client)

    new_state = TaskState.failed
    new_message = "HI THERE"
    new_output = {"a": 3}

    assert task.state != new_state
    assert task.status_message != new_message
    assert task.output != new_output

    response = InvocableResponse(status=task)

    response.status.state = new_state
    response.status.status_message = new_message
    response.status.output = new_output

    # Sanity check: we'll prove that caling task.check() resets this..
    task.refresh()

    # Assert not equal
    assert task.state != new_state
    assert task.status_message != new_message
    assert task.output != new_output

    # And override again
    response.status.state = TaskState.failed
    response.status.status_message = new_message
    response.set_data(json=new_output)

    # Now we call post_update
    response.post_update(client)

    # Call task.check
    with pytest.raises(SteamshipError):
        task.refresh()
