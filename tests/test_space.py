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
