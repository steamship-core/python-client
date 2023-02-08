from typing import List

import pytest
from pydantic import BaseModel
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import SteamshipError, Task, TaskState


def schedule_task(client, please_fail: bool = False, dependencies: List[Task] = None) -> Task:
    response = client.post(
        "task/alwaysfail" if please_fail else "task/noop",
        payload={},
        expect=Task[BaseModel],
        as_background_task=True,
        wait_on_tasks=dependencies,
    )
    assert response is not None
    assert response.state == TaskState.waiting
    assert response.task_id is not None
    return response


def test_task_wait_callback():
    """Test basic connection"""
    client = get_steamship_client()

    task1 = schedule_task(client)

    retries_checked = 0

    def on_task_check(retry_number, total_sec, task):
        nonlocal retries_checked
        retries_checked = retries_checked + 1
        assert retry_number
        assert retry_number > 0
        assert total_sec
        assert total_sec > 0
        assert task.task_id == task1.task_id

    task1.wait(on_each_refresh=on_task_check)
    assert retries_checked > 0
    assert task1.state == TaskState.succeeded


def test_task_dependencies_parallel_success():
    """Test basic connection"""
    client = get_steamship_client()

    task1 = schedule_task(client)
    task2 = schedule_task(client)
    task3 = schedule_task(client, dependencies=[task1, task2])

    task1.wait()
    assert task1.state == TaskState.succeeded

    task2.wait()
    assert task2.state == TaskState.succeeded

    task3.wait()
    assert task3.state == TaskState.succeeded


def test_task_dependencies_parallel_failure():
    """Test basic connection"""
    client = get_steamship_client()

    task1 = schedule_task(client)
    task2 = schedule_task(client, please_fail=True)
    task3 = schedule_task(client, dependencies=[task1, task2])

    task1.wait()
    assert task1.state == TaskState.succeeded

    with pytest.raises(SteamshipError):
        task2.wait()  # It failed!

    with pytest.raises(SteamshipError):
        task3.wait()  # It failed too -- because of the rollup!
