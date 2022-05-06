import json

from steamship import MimeTypes, DocTag
from steamship.base.response import TaskState
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags.tag import Tag
from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_query():
    client = _steamship()
    a = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A", tags=[Tag.CreateRequest(name="BlockTag")]),
            Block.CreateRequest(text="B")
        ]
    ).data
    assert (a.id is not None)
    a = a.refresh().data
    b = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A"),
            Block.CreateRequest(text="B", tags=[Tag.CreateRequest(name="Test")])
        ],
        tags=[
            Tag.CreateRequest(name="FileTag")
        ]
    ).data
    assert (b.id is not None)
    b = b.refresh().data

    blocks = Block.query(client=client, tagFilterQuery='blocktag and name "BlockTag"').data.blocks
    assert (len(blocks)==1)
    assert(blocks[0].id == a.blocks[0].id)

    blocks = Block.query(client=client, tagFilterQuery='blocktag and name "Test"').data.blocks
    assert (len(blocks) == 1)
    assert (blocks[0].id == b.blocks[1].id)



    a.delete()
    b.delete()