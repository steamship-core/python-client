from __future__ import annotations

import pytest

from steamship import SteamshipError
from steamship.base import Response, Task

TEST_DATA = {"test": "test"}


def test_no_data_response():
    response = Response[dict](error=SteamshipError())

    with pytest.raises(SteamshipError):
        _ = response.data


def test_async_response():
    response = Response[dict](task=Task())
    assert response.data is None
    response.update(Response[dict](task=Task(), data_=TEST_DATA))
    assert response.data is not None
    assert response.data["test"] == "test"


def test_data_response():
    response = Response[dict](data_=TEST_DATA)
    assert response.data is not None
    assert response.data["test"] == "test"
