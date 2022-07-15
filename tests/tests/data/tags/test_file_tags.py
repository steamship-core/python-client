import pytest

from steamship import Block, File, MimeTypes
from steamship.client import Steamship
from steamship.data.tags import Tag


@pytest.mark.usefixtures("client")
def test_file_tag(client: Steamship):
    a = client.upload(content="A", mime_type=MimeTypes.MKD).data
    assert a.id is not None
    assert a.mime_type == MimeTypes.MKD

    _ = Tag.create(client, file_id=a.id, name="test1").data
    _ = Tag.create(client, file_id=a.id, name="test2").data

    tags = Tag.list_public(client, file_id=a.id)
    assert tags.data is not None
    assert tags.data.tags is not None
    assert len(tags.data.tags) == 2

    must = ["test1", "test2"]
    for tag in tags.data.tags:
        assert tag.name in must
        must.remove(tag.name)
    assert len(must) == 0

    for tag in tags.data.tags:
        if tag.name == "test1":
            tag.delete()

    tags = Tag.list_public(client, file_id=a.id)
    assert tags.data is not None
    assert tags.data.tags is not None
    assert len(tags.data.tags) == 1

    must = ["test2"]
    for tag in tags.data.tags:
        assert tag.name in must
        must.remove(tag.name)
    assert len(must) == 0

    tags.data.tags[0].delete()

    tags = Tag.list_public(client, file_id=a.id)
    assert tags.data is not None
    assert tags.data.tags is not None
    assert len(tags.data.tags) == 0

    a.delete()


def test_query(client: Steamship):
    a = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A", tags=[Tag.CreateRequest(name="BlockTag")]),
            Block.CreateRequest(text="B"),
        ],
    ).data
    assert a.id is not None
    a = a.refresh().data
    b = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A"),
            Block.CreateRequest(text="B", tags=[Tag.CreateRequest(name="Test")]),
        ],
        tags=[Tag.CreateRequest(name="FileTag")],
    ).data
    assert b.id is not None
    b = b.refresh().data

    tags = Tag.query(client=client, tag_filter_query='blocktag and name "BlockTag"').data.tags
    assert len(tags) == 1
    assert tags[0].id == a.blocks[0].tags[0].id

    tags = Tag.query(client=client, tag_filter_query='blocktag and name "Test"').data.tags
    assert len(tags) == 1
    assert tags[0].id == b.blocks[1].tags[0].id

    a.delete()
    b.delete()
