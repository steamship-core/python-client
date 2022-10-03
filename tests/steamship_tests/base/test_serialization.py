import json

import pytest

from steamship.client import Steamship
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags.tag import Tag


@pytest.mark.usefixtures("client")
def test_dict_method_should_not_include_client(client: Steamship):
    block = Block(client=client, text="Hi")
    d = block.dict()
    assert isinstance(d, dict)
    assert "client" not in d

    d = block.dict(exclude={"foo"})
    assert isinstance(d, dict)
    assert "client" not in d


@pytest.mark.usefixtures("client")
def test_serialize_client_to_json_works(client: Steamship):
    assert "use" not in client.dict().keys()
    assert "use_plugin" not in client.dict().keys()

    j = json.dumps(client.dict())  # this will fail if `use` or `use_plugin` are output by dict()
    assert j is not None


@pytest.mark.usefixtures("client")
def test_serialize_many_models(client: Steamship):
    json.dumps(Block(client=client).dict())
    json.dumps(Block(client=client, tags=[Tag(client=client)]).dict())
    json.dumps(Tag(client=client).dict())
    json.dumps(File(client=client).dict())
    json.dumps(File(client=client, tags=[Tag(client=client)]).dict())
    json.dumps(File(client=client, tags=[Tag(client=client)], blocks=[Block(client=client)]).dict())
    json.dumps(
        File(
            client=client,
            tags=[Tag(client=client)],
            blocks=[Block(client=client, tags=[Tag(client=client)])],
        ).dict()
    )
