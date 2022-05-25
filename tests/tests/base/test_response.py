from __future__ import annotations

import pytest

from steamship import SteamshipError
from steamship.base import Response


def test_no_data_response():
    response = Response[dict](error=SteamshipError())

    with pytest.raises(SteamshipError):
        _ = response.data


def test_data_response():
    response = Response[dict](data_={"test": "test"})

    assert response.data is not None
    assert response.data["test"] == "test"
