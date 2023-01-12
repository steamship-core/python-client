from steamship_tests.utils.fixtures import get_steamship_client

from steamship import File, PluginInstance, Steamship
from steamship.data import TagKind, TagValueKey

_TEST_EMBEDDER = "test-embedder"


def count_embeddings(file: File):
    embeddings = 0
    for block in file.blocks:
        for tag in block.tags:
            if tag.kind == TagKind.EMBEDDING:
                embeddings += 1
    return embeddings


def basic_embeddings(plugin_instance: PluginInstance):
    e1 = plugin_instance.tag("This is a test")
    e1b = plugin_instance.tag("Banana")
    e1.wait()
    e1b.wait()
    assert count_embeddings(e1.output.file) == 1
    assert count_embeddings(e1b.output.file) == 1
    assert len(e1.output.file.blocks[0].tags[0].value[TagValueKey.VECTOR_VALUE]) > 1

    e2 = plugin_instance.tag("This is a test")
    e2.wait()
    assert count_embeddings(e2.output.file) == 1
    assert len(e2.output.file.blocks[0].tags[0].value[TagValueKey.VECTOR_VALUE]) == len(
        e1.output.file.blocks[0].tags[0].value[TagValueKey.VECTOR_VALUE]
    )

    e4 = plugin_instance.tag("This is a test")
    e4.wait()
    assert count_embeddings(e4.output.file) == 1


def test_basic_embeddings():
    client = get_steamship_client()
    plugin_instance = PluginInstance.create(client, plugin_handle=_TEST_EMBEDDER)
    basic_embeddings(plugin_instance)


def basic_embedding_search(steamship: Steamship, plugin_instance: str):
    docs = [
        "Armadillo shells are bulletproof.",
        "Dolphins sleep with one eye open.",
        "Alfred Hitchcock was frightened of eggs.",
        "Jonathan can help you with new employee onboarding",
        "The code for the New York office is 1234",
    ]
    query = "Who should I talk to about new employee setup?"
    results = steamship.embed_and_search(query, docs, plugin_instance=plugin_instance)
    assert len(results.items) == 1
    assert results.items[0].value.value == "Jonathan can help you with new employee onboarding"


def test_basic_embedding_search():
    client = get_steamship_client()
    plugin_instance = PluginInstance.create(client, plugin_handle=_TEST_EMBEDDER)
    basic_embedding_search(client, plugin_instance.handle)
