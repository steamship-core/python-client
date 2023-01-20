import pytest

from steamship.client import Steamship
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags.tag import Tag


@pytest.mark.usefixtures("client")
def test_query(client: Steamship):
    a = File.create(
        client=client,
        blocks=[
            Block(text="A", tags=[Tag(kind="BlockTag")]),
            Block(text="B"),
        ],
    )
    assert a.id is not None
    a = a.refresh()
    b = File.create(
        client=client,
        blocks=[
            Block(text="A"),
            Block(text="B", tags=[Tag(kind="Test")]),
        ],
        tags=[Tag(kind="FileTag")],
    )
    assert b.id is not None
    b = b.refresh()

    blocks = Block.query(client=client, tag_filter_query='blocktag and kind "BlockTag"').blocks
    assert len(blocks) == 1
    assert blocks[0].id == a.blocks[0].id

    blocks = Block.query(client=client, tag_filter_query='blocktag and kind "Test"').blocks
    assert len(blocks) == 1
    assert blocks[0].id == b.blocks[1].id

    a.delete()
    b.delete()
