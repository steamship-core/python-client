from steamship import PluginInstance
from steamship.base import Client

from tests.client.helpers import _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

_TEST_EMBEDDER = "test-embedder"


def basic_embeddings(steamship: Client, pluginInstance: str):
    e1 = steamship.embed(["This is a test"], pluginInstance=pluginInstance)
    e1b = steamship.embed(["Banana"], pluginInstance=pluginInstance)
    assert (len(e1.data.embeddings) == 1)
    assert (len(e1.data.embeddings[0]) > 1)

    e2 = steamship.embed(["This is a test"], pluginInstance=pluginInstance)
    assert (len(e2.data.embeddings) == 1)
    assert (len(e2.data.embeddings[0]) == len(e1.data.embeddings[0]))

    e4 = steamship.embed(["This is a test"], pluginInstance=pluginInstance)
    assert (len(e4.data.embeddings) == 1)


def test_basic_embeddings():
    pluginInstance = PluginInstance.create(_steamship(), pluginHandle=_TEST_EMBEDDER).data
    basic_embeddings(_steamship(), pluginInstance.handle)


def basic_embedding_search(steamship: Client, pluginInstance: str):
    docs = [
        "Armadillo shells are bulletproof.",
        "Dolphins sleep with one eye open.",
        "Alfred Hitchcock was frightened of eggs.",
        "Jonathan can help you with new employee onboarding",
        "The code for the New York office is 1234",
    ]
    query = "Who should I talk to about new employee setup?"
    results = steamship.embed_and_search(query, docs, pluginInstance=pluginInstance)
    assert (len(results.data.hits) == 1)
    assert (results.data.hits[0].value == "Jonathan can help you with new employee onboarding")


def test_basic_embedding_search():
    pluginInstance = PluginInstance.create(_steamship(), pluginHandle=_TEST_EMBEDDER).data
    basic_embedding_search(_steamship(), pluginInstance.handle)
