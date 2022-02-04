from steamship.base import Client
from .helpers import _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

_TEST_EMBEDDER = "test-embedder-v1"


def basic_embeddings(steamship: Client, model: str):
    e1 = steamship.embed(["This is a test"], model=model)
    e1b = steamship.embed(["Banana"], model=model)
    assert (len(e1.data.embeddings) == 1)
    assert (len(e1.data.embeddings[0]) > 1)

    e2 = steamship.embed(["This is a test"], model=model)
    assert (len(e2.data.embeddings) == 1)
    assert (len(e2.data.embeddings[0]) == len(e1.data.embeddings[0]))

    e4 = steamship.embed(["This is a test"], model=model)
    assert (len(e4.data.embeddings) == 1)


def test_basic_embeddings():
    basic_embeddings(_steamship(), _TEST_EMBEDDER)


def basic_embedding_search(steamship: Client, model: str):
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
    assert (len(results.data.hits) == 1)
    assert (results.data.hits[0].value == "Jonathan can help you with new employee onboarding")


def test_basic_embedding_search():
    basic_embeddings(_steamship(), _TEST_EMBEDDER)
