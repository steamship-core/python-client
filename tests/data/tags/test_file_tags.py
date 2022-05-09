from steamship import MimeTypes, File, Block
from steamship.data.tags import Tag

from tests.client.helpers import _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_file_tag():
    steamship = _steamship()
    a = steamship.upload(content="A", mimeType=MimeTypes.MKD).data
    assert a.id is not None
    assert a.mimeType == MimeTypes.MKD

    t1 = Tag.create(steamship, fileId=a.id, name="test1").data
    t2 = Tag.create(steamship, fileId=a.id, name="test2").data

    tags = Tag.listPublic(steamship, fileId=a.id)
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

    tags = Tag.listPublic(steamship, fileId=a.id)
    assert tags.data is not None
    assert tags.data.tags is not None
    assert len(tags.data.tags) == 1

    must = ["test2"]
    for tag in tags.data.tags:
        assert tag.name in must
        must.remove(tag.name)
    assert len(must) == 0

    tags.data.tags[0].delete()

    tags = Tag.listPublic(steamship, fileId=a.id)
    assert tags.data is not None
    assert tags.data.tags is not None
    assert len(tags.data.tags) == 0

    a.delete()


def test_query():
    client = _steamship()
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

    tags = Tag.query(
        client=client, tagFilterQuery='blocktag and name "BlockTag"'
    ).data.tags
    assert len(tags) == 1
    assert tags[0].id == a.blocks[0].tags[0].id

    tags = Tag.query(client=client, tagFilterQuery='blocktag and name "Test"').data.tags
    assert len(tags) == 1
    assert tags[0].id == b.blocks[1].tags[0].id

    a.delete()
    b.delete()
