import pytest
import os
import random
import string
import contextlib

from nludb import NLUDB, EmbeddingModels, EmbeddingIndex
from .helpers import _random_index, _random_name, _nludb

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

def test_connect():
    """Test basic connection"""
    client = _nludb()
    assert(client.config is not None)
    assert(client.config.profile == "test")
    assert(client.config.apiKey is not None)
