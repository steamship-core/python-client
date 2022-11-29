"""Tests the Embedding Index Snapshot functionality.

When we finish re-factoring the index code in the Engine, these tests can be deleted.
For now, it's useful to have them as-is, as they target a detail of index operation that the old interface
captures, but the new interface does not.
"""
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import PluginInstance
from steamship.base import TaskState
from steamship.data.embeddings import EmbeddingIndex, IndexSnapshotRequest, IndexSnapshotResponse

_TEST_EMBEDDER = "test-embedder"


def _insert(index, items):
    for item in items:
        index.insert(item, "TestId", "TestType", [1, 2, 3])

    # Now embed
    task = index.embed()
    task.wait()
    task.refresh()
    assert task.state == TaskState.succeeded


def _snapshot(index, window_size=None):
    if window_size is None:
        task = index.create_snapshot()
        task.wait()
        task.refresh()
    else:
        # We do this manually so as not to clutter the end-user visible
        # API with debug/testing parameters
        req = IndexSnapshotRequest(index_id=index.id, window_size=window_size)
        task = index.client.post(
            "embedding-index/snapshot/create",
            req,
            expect=IndexSnapshotResponse,
        )
        task.wait()
        task.refresh()


def test_snapshot_create():
    steamship = get_steamship_client()

    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER)
    index = EmbeddingIndex.create(
        client=steamship,
        embedder_plugin_instance_handle=plugin_instance.handle,
    )

    _insert(index, ["Oranges are orange."])
    search_results = index.search("What color are oranges?", include_metadata=True)
    search_results.wait()
    items = search_results.output.items
    assert len(items) == 1
    assert items[0].value.index_source == "index"
    assert items[0].value.value == "Oranges are orange."
    assert items[0].value.external_id == "TestId"
    assert items[0].value.external_type == "TestType"
    assert len(items[0].value.metadata) == 3

    _snapshot(index)
    search_results = index.search("What color are oranges?", include_metadata=True)
    search_results.wait()
    items = search_results.output.items
    assert len(items) == 1
    assert items[0].value.index_source == "snapshot"
    assert items[0].value.value == "Oranges are orange."
    assert items[0].value.external_id == "TestId"
    assert items[0].value.external_type == "TestType"
    assert len(items[0].value.metadata) == 3

    _insert(index, ["Apples are red."])
    search_results = index.search("What color are apples?", include_metadata=True)
    search_results.wait()
    items = search_results.output.items
    assert len(items) == 1
    assert items[0].value.index_source == "index"
    assert items[0].value.value == "Apples are red."
    assert items[0].value.external_id == "TestId"
    assert items[0].value.external_type == "TestType"
    assert len(items[0].value.metadata) == 3

    _snapshot(index)
    search_results = index.search("What color are apples?", include_metadata=True)
    search_results.wait()
    items = search_results.output.items
    assert len(items) == 1
    assert items[0].value.index_source == "snapshot"
    assert items[0].value.value == "Apples are red."
    assert items[0].value.external_id == "TestId"
    assert items[0].value.external_type == "TestType"
    assert len(items[0].value.metadata) == 3

    index.delete()
    steamship = get_steamship_client()

    index = EmbeddingIndex.create(
        client=steamship,
        embedder_plugin_instance_handle=plugin_instance.handle,
    )

    sentences = []
    for i in range(15):
        sentences.append(f"Orange number {i} is as good as the last")

    sent = "Is orange number 13 Any good?"
    _insert(index, sentences)

    search_results = index.search(sent, include_metadata=True)
    search_results.wait()
    items = search_results.output.items
    assert len(items) == 1
    assert items[0].value.index_source == "index"
    assert items[0].value.value == "Orange number 13 is as good as the last"
    assert items[0].value.external_id == "TestId"
    assert items[0].value.external_type == "TestType"
    assert len(items[0].value.metadata) == 3

    _snapshot(index, window_size=2)
    search_results = index.search(sent, include_metadata=True)
    search_results.wait()
    items = search_results.output.items
    assert len(items) == 1
    assert items[0].value.index_source == "snapshot"
    assert items[0].value.value == "Orange number 13 is as good as the last"
    assert items[0].value.external_id == "TestId"
    assert items[0].value.external_type == "TestType"
    assert len(items[0].value.metadata) == 3

    index.delete()
