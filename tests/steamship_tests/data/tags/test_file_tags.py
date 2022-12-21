import pytest
from pydantic import ValidationError

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

    tags = Tag.query(client, tag_filter_query=f'file_id "{a.id}"').tags
    assert tags is not None
    assert len(tags) == 2

    must = ["test1", "test2"]
    for tag in tags:
        assert tag.kind in must
        must.remove(tag.kind)
    assert len(must) == 0

    for tag in tags:
        if tag.kind == "test1":
            tag.delete()

    Tag.create(client, file_id=a.id, kind="test3")

    tags = Tag.query(client, tag_filter_query=f'file_id "{a.id}"').tags
    assert tags is not None
    assert len(tags) == 2

    must = ["test2", "test3"]
    for tag in tags:
        assert tag.kind in must
        must.remove(tag.kind)
    assert len(must) == 0

    tags[0].delete()
    tags[1].delete()

    tags = Tag.query(client, tag_filter_query=f'file_id "{a.id}"').tags
    assert tags is not None
    assert len(tags) == 0

    Tag.create(
        client,
        file_id=a.id,
        kind="test4",
        value={"test_str": "str", "test_int": 1, "test_float": 2.2},
    )
    tags = Tag.query(client, tag_filter_query=f'file_id "{a.id}"').tags
    assert tags is not None
    assert len(tags) == 1
    assert tags[0].kind == "test4"

    with pytest.raises(ValidationError):
        Tag.create(client, file_id=a.id, kind="test3", value=23)
    with pytest.raises(ValidationError):
        Tag.create(client, file_id=a.id, kind="test3", value="invalid")

    a.delete()


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

    tags = Tag.query(client=client, tag_filter_query='blocktag and kind "BlockTag"').tags
    assert len(tags) == 1
    assert tags[0].id == a.blocks[0].tags[0].id

    tags = Tag.query(client=client, tag_filter_query='blocktag and kind "Test"').tags
    assert len(tags) == 1
    assert tags[0].id == b.blocks[1].tags[0].id

    a.delete()
    b.delete()
