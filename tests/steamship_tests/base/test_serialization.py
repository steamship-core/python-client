import pytest

from steamship.client import Steamship
from steamship.data.block import Block


@pytest.mark.usefixtures("client")
def test_dict_method_should_not_include_client(client: Steamship):
    block = Block(client=client, text="Hi")
    d = block.dict()
    assert isinstance(d, dict)
    assert "client" not in d

    d = block.dict(exclude={"foo"})
    assert isinstance(d, dict)
    assert "client" not in d
