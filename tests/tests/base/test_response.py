from __future__ import annotations

import pytest

from steamship import SteamshipError
from steamship.base import Response, Task, TaskState

TEST_DATA = {"test": "test"}


def test_no_data_response():
    response = Response[dict](error=SteamshipError())

    with pytest.raises(SteamshipError):
        _ = response.data


def test_async_response():
    response = Response[dict](task=Task())
    with pytest.raises(SteamshipError):
        _ = response.data

    response.update(Response[dict](task=Task(state=TaskState.succeeded), data_=TEST_DATA))
    assert response.data is not None
    assert response.data == TEST_DATA

    for ongoing_state in (TaskState.running, TaskState.waiting):
        response = Response[dict](task=Task(state=ongoing_state))
        with pytest.raises(SteamshipError):
            _ = response.data

        response.update(Response[dict](task=Task(state=ongoing_state), data_=TEST_DATA))
        assert response.data is not None
        assert response.data == TEST_DATA

    response = Response[dict](task=Task(state=TaskState.failed))
    with pytest.raises(SteamshipError):
        _ = response.data

    response.update(Response[dict](task=Task(state=TaskState.failed), data_=TEST_DATA))
    with pytest.raises(SteamshipError):
        _ = response.data


def test_data_response():
    response = Response[dict](data_=TEST_DATA)
    assert response.data is not None
    assert response.data == TEST_DATA
