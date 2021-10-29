from nludb.types.async_task import NludbTaskStatus
import pytest
from os import path
from .helpers import _random_name, _nludb
from nludb import NLUDB, BlockTypes, FileFormats

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_file_tag():
    nludb = _nludb()
    name_a = "{}.mkd".format(_random_name())
    a = nludb.upload(
      name=name_a,
      content="A",
      format=FileFormats.MKD
    )
    assert(a.id is not None)
    assert(a.name == name_a)
    assert(a.format == FileFormats.MKD)

    a.add_tags(['test1', 'test2'])

    tags = a.list_tags().data.tags
    print(tags)
    assert(len(tags) == 2)

    must = ['test1', 'test2']
    for tag in tags:
      assert(tag.name in must)
      must.remove(tag.name)
    assert(len(must) == 0)        

    a.remove_tags(['test1'])

    tags = a.list_tags().data.tags
    print(tags)
    assert(len(tags) == 1)

    must = ['test2']
    for tag in tags:
      assert(tag.name in must)
      must.remove(tag.name)
    assert(len(must) == 0)        

    # What happens when you move one that doesn't exist
    with pytest.raises(Exception):
      a.remove_tags(['test1'])

    # Remove the last
    a.remove_tags(['test2'])

    tags = a.list_tags().data.tags
    print(tags)
    assert(len(tags) == 0)

    a.delete()

