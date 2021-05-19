from nludb.types.async_task import NludbTaskStatus
import pytest
import os
import random
import string
import contextlib
from .helpers import _random_index, _random_name, _nludb

from nludb import NLUDB, EmbeddingModels, EmbeddingIndex

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_file_upload():
    nludb = _nludb()

    name_a = "{}.txt".format(_random_name())
    a = nludb.upload_file(
        name=name_a,
        content="A"
    )
    assert(a.id is not None)

    name_b = "{}.txt".format(_random_name())
    b = nludb.upload_file(
        name=name_b,
        content="B"
    )
    assert(b.id is not None)
    
    assert(a.id != b.id)

    a.delete()
    b.delete()