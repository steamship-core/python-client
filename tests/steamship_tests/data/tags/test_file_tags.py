import pytest

from steamship import Block, File, MimeTypes
from steamship.client import Steamship
from steamship.data.tags import Tag


@pytest.mark.usefixtures("client")
def test_file_tag(client: Steamship):
    a = File.create(
        client,
        content="A",
        mime_type=MimeTypes.MKD,
    )
    assert a.id is not None
    assert a.mime_type == MimeTypes.MKD

    _ = Tag.create(client, file_id=a.id, kind="test1")
    _ = Tag.create(client, file_id=a.id, kind="test2")

    tags = Tag.query(client, tag_filter_query=f'file_id "{a.id}"')
    assert tags.tags is not None
    assert len(tags.tags) == 2

    must = ["test1", "test2"]
    for tag in tags.tags:
        assert tag.kind in must
        must.remove(tag.kind)
    assert len(must) == 0

    for tag in tags.tags:
        if tag.kind == "test1":
            tag.delete()

    tags = Tag.query(client, tag_filter_query=f'file_id "{a.id}"')
    assert tags is not None
    assert tags.tags is not None
    assert len(tags.tags) == 1

    must = ["test2"]
    for tag in tags.tags:
        assert tag.kind in must
        must.remove(tag.kind)
    assert len(must) == 0

    tags.tags[0].delete()

    tags = Tag.query(client, tag_filter_query=f'file_id "{a.id}"')
    assert tags is not None
    assert tags.tags is not None
    assert len(tags.tags) == 0

    a.delete()


def test_query(client: Steamship):
    a = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A", tags=[Tag.CreateRequest(kind="BlockTag")]),
            Block.CreateRequest(text="B"),
        ],
    )
    assert a.id is not None
    a = a.refresh()
    b = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A"),
            Block.CreateRequest(text="B", tags=[Tag.CreateRequest(kind="Test")]),
        ],
        tags=[Tag.CreateRequest(kind="FileTag")],
    )
    assert b.id is not None
    b = b.refresh()

    tags = Tag.query(client=client, tag_filter_query='blocktag and kind "BlockTag"').tags
    assert len(tags) == 1
    assert tags[0].id == a.blocks[0].tags[0].id

    tags = Tag.query(client=client, tag_filter_query='blocktag and kind "Test"').tags
    assert len(tags) == 1
    assert tags[0].id == b.blocks[1].tags[0].id

    a.delete()
    b.delete()
