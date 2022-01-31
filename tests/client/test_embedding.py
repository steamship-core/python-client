import pytest
from .helpers import _random_index, _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

_TEST_EMBEDDER = "test-embedder-v1"

def test_basic_embeddings():
    steamship = _steamship()

    e1 = steamship.embed(["This is a test"], model=_TEST_EMBEDDER)
    e1b = steamship.embed(["Banana"], model=_TEST_EMBEDDER)
    assert(len(e1.data.embeddings) == 1)
    assert(len(e1.data.embeddings[0]) > 1)

    e2 = steamship.embed(["This is a test"], model=_TEST_EMBEDDER)
    assert(len(e2.data.embeddings) == 1)
    assert(len(e2.data.embeddings[0]) == len(e1.data.embeddings[0]))

    e4 = steamship.embed(["This is a test"], model=_TEST_EMBEDDER)
    assert(len(e4.data.embeddings) == 1)

def test_basic_embedding_search():
    steamship = _steamship()
    docs = [
        "Armadillo shells are bulletproof.",
        "Dolphins sleep with one eye open.",
        "Alfred Hitchcock was frightened of eggs.",
        "Jonathan can help you with new employee onboarding",
        "The code for the New York office is 1234",
    ]
    query = "Who should I talk to about new employee setup?"
    results = steamship.embed_and_search(query, docs, model=_TEST_EMBEDDER)
    assert(len(results.data.hits) == 1)
    assert(results.data.hits[0].value == "Jonathan can help you with new employee onboarding")
