from steamship import MimeTypes
from steamship.data.tags import Tag

from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_file_tag():
    steamship = _steamship()
    name_a = "{}.mkd".format(_random_name())
    a = steamship.upload(
        name=name_a,
        content="A",
        mimeType=MimeTypes.MKD
    ).data
    assert (a.id is not None)
    assert (a.name == name_a)
    assert (a.mimeType == MimeTypes.MKD)

    t1 = Tag.create(steamship, fileId=a.id, name="test1").data
    t2 = Tag.create(steamship, fileId=a.id, name="test2").data

    tags = Tag.listPublic(steamship, fileId=a.id)
    assert (tags.data is not None)
    assert (tags.data.tags is not None)
    assert (len(tags.data.tags) == 2)

    must = ['test1', 'test2']
    for tag in tags.data.tags:
        assert (tag.name in must)
        must.remove(tag.name)
    assert (len(must) == 0)

    for tag in tags.data.tags:
        if tag.name == 'test1':
            tag.delete()

    tags = Tag.listPublic(steamship, fileId=a.id)
    assert (tags.data is not None)
    assert (tags.data.tags is not None)
    assert (len(tags.data.tags) == 1)

    must = ['test2']
    for tag in tags.data.tags:
        assert (tag.name in must)
        must.remove(tag.name)
    assert (len(must) == 0)

    tags.data.tags[0].delete()

    tags = Tag.listPublic(steamship, fileId=a.id)
    assert (tags.data is not None)
    assert (tags.data.tags is not None)
    assert (len(tags.data.tags) == 0)

    a.delete()
