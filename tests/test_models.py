from nludb.types.async_task import NludbTaskStatus
from nludb.types.model import ModelAdapterType
import pytest
import os
import random
import string
import contextlib

from nludb import NLUDB, ModelType

from .helpers import _random_index, _random_name, _nludb

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

def test_model_create():
    nludb = _nludb()
    name = _random_name()

    my_models = nludb.models.listPrivate().data
    orig_count = len(my_models.models)

    # Should require name
    with pytest.raises(Exception):
        index = nludb.models.create(
            description = "This is just for test",
            modelType = ModelType.embedder,
            url = "http://foo",
            adapterType = ModelAdapterType.nludbDocker,
            isPublic = True
        )

    # Should require description
    with pytest.raises(Exception):
        index = nludb.models.create(
            name = "Test Model",
            modelType = ModelType.embedder,
            url = "http://foo",
            adapterType = ModelAdapterType.nludbDocker,
            isPublic = True
        )

    # Should require model type
    with pytest.raises(Exception):
        index = nludb.models.create(
            name = "Test Model",
            description = "This is just for test",
            url = "http://foo",
            adapterType = ModelAdapterType.nludbDocker,
            isPublic = True
        )

    # Should require url
    with pytest.raises(Exception):
        index = nludb.models.create(
            name = "Test Model",
            description = "This is just for test",
            modelType = ModelType.embedder,
            adapterType = ModelAdapterType.nludbDocker,
            isPublic = True
        )

    # Should require adapter type
    with pytest.raises(Exception):
        index = nludb.models.create(
            name = "Test Model",
            description = "This is just for test",
            modelType = ModelType.embedder,
            url = "http://foo",
            isPublic = True
        )

    # Should require is public
    with pytest.raises(Exception):
        index = nludb.models.create(
            name = "Test Model",
            description = "This is just for test",
            modelType = ModelType.embedder,
            url = "http://foo",
            adapterType = ModelAdapterType.nludbDocker,
        )

    my_models = nludb.models.listPrivate().data
    assert(len(my_models.models) == orig_count)

    model = nludb.models.create(
        name = _random_name(),
        description = "This is just for test",
        modelType = ModelType.embedder,
        url = "http://foo",
        adapterType = ModelAdapterType.nludbDocker,
        isPublic = False
    ).data

    my_models = nludb.models.listPrivate().data
    assert(len(my_models.models) == orig_count+1)

    # No upsert doesn't work
    with pytest.raises(Exception):
      model = nludb.models.create(
          name = model.name,
          description = "This is just for test",
          modelType = ModelType.embedder,
          url = "http://foo",
          adapterType = ModelAdapterType.nludbDocker,
          isPublic = False
      ).data

    # Upsert does work
    model2 = nludb.models.create(
        name = model.name,
        description = "This is just for test 2",
        modelType = ModelType.embedder,
        url = "http://foo",
        adapterType = ModelAdapterType.nludbDocker,
        isPublic = False,
        upsert = True
    ).data

    assert(model2.id == model.id)

    my_models = nludb.models.listPrivate().data
    assert(len(my_models.models) == orig_count+1)

    assert(model2.id in [model.id for model in my_models.models])
    assert(model2.description in [model.description for model in my_models.models])

    # assert(my_models.models[0].description != model.description)

    nludb.models.delete(model.id)

    my_models = nludb.models.listPrivate().data
    assert(len(my_models.models) == orig_count)

def test_model_public():
    nludb = _nludb()
    name = _random_name()

    my_models = nludb.models.listPublic().data
    orig_count = len(my_models.models)
    assert(len(my_models.models) > 0, True)

    # Make sure they can't be deleted.
    with pytest.raises(Exception):    
      nludb.models.delete(my_models.models[0].id)
    
