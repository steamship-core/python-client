from steamship import PluginInstance, File
from steamship.base import Client

from tests.client.helpers import _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

_TEST_EMBEDDER = "test-embedder"

def count_embeddings(file: File):
    embeddings = 0
    for block in file.blocks:
        for tag in block.tags:
            if tag.kind == 'text' and tag.name == 'embedding':
                embeddings += 1
    return embeddings

def basic_embeddings(steamship: Client, pluginInstance: str):
    e1 = steamship.tag("This is a test", pluginInstance=pluginInstance)
    e1b = steamship.tag("Banana", pluginInstance=pluginInstance)
    e1.wait()
    e1b.wait()
    assert (count_embeddings(e1.data.file) == 1)
    assert (count_embeddings(e1b.data.file) == 1)
    assert (len(e1.data.file.blocks[0].tags[0].value['embedding']) > 1)

    e2 = steamship.tag("This is a test", pluginInstance=pluginInstance)
    e2.wait()
    assert (count_embeddings(e2.data.file) == 1)
    assert (len(e2.data.file.blocks[0].tags[0].value['embedding']) == len(e1.data.file.blocks[0].tags[0].value['embedding']))

    e4 = steamship.tag("This is a test", pluginInstance=pluginInstance)
    e4.wait()
    assert (count_embeddings(e4.data.file) == 1)


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
    assert (len(results.data.items) == 1)
    assert (results.data.items[0].value.value == "Jonathan can help you with new employee onboarding")


def test_basic_embedding_search():
    pluginInstance = PluginInstance.create(_steamship(), pluginHandle=_TEST_EMBEDDER).data
    basic_embedding_search(_steamship(), pluginInstance.handle)
