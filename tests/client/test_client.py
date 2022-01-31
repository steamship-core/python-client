import pytest
import os
import random
import string
import contextlib

from steamship import Steamship, EmbeddingIndex
from .helpers import _random_index, _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

def test_connect():
    """Test basic connection"""
    client = _steamship()
    assert(client.config is not None)
    assert(client.config.profile == "test")
    assert(client.config.apiKey is not None)
