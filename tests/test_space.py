import pytest
from nludb import EmbeddingModels
from .helpers import _random_index, _random_name, _nludb, qa_model, sim_model
from nludb import Space


__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_default_space():
  client = _nludb()
  space = Space.get(client=client).data
  assert(space is not None)
  assert(space.handle == 'default')

def test_create_use_delete_space():
  client = _nludb()
  default = Space.get(client=client).data
  space1 = Space.create(client=client, name="Test", handle="test").data
  space2 = Space.create(client=client, name="Test", handle="test2").data

  assert(space1 is not None)
  assert(space1.handle == 'test')

  assert(space2 is not None)
  assert(space2.handle == 'test2')

  assert(space2.id != space1.id)
  assert(space1.id != default.id)
  assert(space2.id != default.id)

  space1a = Space.get(client=client, spaceId=space1.id).data
  space1b = Space.get(client=client, spaceHandle=space1.handle).data
  space1c = Space.get(client=client, space=space1).data

  assert(space1.id != space1a.id)
  assert(space1.id != space1b.id)
  assert(space1.id != space1c.id)
