from nludb.types.async_task import NludbTaskStatus
import pytest
import os
import random
import string
import contextlib

from nludb import NLUDB, ClassifierModels, Classifier
from .helpers import _random_index, _random_name, _nludb

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

def test_classifier_create():
  nludb = _nludb()
  name = _random_name()

  # Should require name
  with pytest.raises(Exception):
    index = nludb.create_classifier(
      model=ClassifierModels.HF_ZERO_SHOT_LBART
    )

  # Should require model
  with pytest.raises(Exception):
    index = nludb.create_classifier(
      name="Test Index"
    )

  classifier = nludb.create_classifier(
    name="Test 2",
    model=ClassifierModels.HF_ZERO_SHOT_LBART,
    save=False
  )
  assert classifier is not None

  # Missing labels as a zero shot
  with pytest.raises(Exception):
      results = classifier.classify(docs=["Jurassic Park"])

  # Missing docs
  with pytest.raises(Exception):
      results = classifier.classify(labels=["Jurassic Park"])

  # Create one and let's use it
  classifier = nludb.create_classifier(
    name="Fruits",
    model=ClassifierModels.HF_ZERO_SHOT_LBART,
    save=False
  )
  assert classifier is not None
  r = classifier.classify(docs=["Banana"], labels=["Movie", "Food", "City"], k=2)
  assert len(r.data.hits) == 1
  assert len(r.data.hits[0]) == 2
  assert r.data.hits[0][0].value == "Food"

  r = classifier.classify(docs=["Banana"], labels=["Movie", "Food", "City"], k=3)
  
  assert len(r.data.hits) == 1
  assert len(r.data.hits[0]) == 3
  assert r.data.hits[0][0].value == "Food"

  r = classifier.classify(docs=["Banana", "Boston"], labels=["Movie", "Food", "City"], k=3)
  assert len(r.data.hits) == 2
  assert len(r.data.hits[0]) == 3
  assert r.data.hits[0][0].value == "Food"
  assert len(r.data.hits[1]) == 3
  assert r.data.hits[1][0].value == "City"
