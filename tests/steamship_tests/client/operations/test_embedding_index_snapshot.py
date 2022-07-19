from steamship_tests.utils.fixtures import get_steamship_client

from steamship import PluginInstance
from steamship.base.response import TaskState
from steamship.data.embeddings import IndexSnapshotRequest, IndexSnapshotResponse

_TEST_EMBEDDER = "test-embedder"


def _insert(index, items):
    for item in items:
        index.insert(item, "TestId", "TestType", [1, 2, 3])

    # Now embed
    task = index.embed()
    task.wait()
    task.refresh()
    assert task.task.state == TaskState.succeeded


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
            asynchronous=True,
        )
        task.wait()
        task.refresh()


def test_snapshot_create():
    steamship = get_steamship_client()

    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER).data
    index = steamship.create_index(plugin_instance=plugin_instance.handle).data

    _insert(index, ["Oranges are orange."])
    search_results = index.search("What color are oranges?", include_metadata=True)
    assert len(search_results.data.items) == 1
    assert search_results.data.items[0].value.index_source == "index"
    assert search_results.data.items[0].value.value == "Oranges are orange."
    assert search_results.data.items[0].value.external_id == "TestId"
    assert search_results.data.items[0].value.external_type == "TestType"
    assert len(search_results.data.items[0].value.metadata) == 3

    _snapshot(index)
    search_results = index.search("What color are oranges?", include_metadata=True)
    assert len(search_results.data.items) == 1
    assert search_results.data.items[0].value.index_source == "snapshot"
    assert search_results.data.items[0].value.value == "Oranges are orange."
    assert search_results.data.items[0].value.external_id == "TestId"
    assert search_results.data.items[0].value.external_type == "TestType"
    assert len(search_results.data.items[0].value.metadata) == 3

    _insert(index, ["Apples are red."])
    search_results = index.search("What color are apples?", include_metadata=True)
    assert len(search_results.data.items) == 1
    assert search_results.data.items[0].value.index_source == "index"
    assert search_results.data.items[0].value.value == "Apples are red."
    assert search_results.data.items[0].value.external_id == "TestId"
    assert search_results.data.items[0].value.external_type == "TestType"
    assert len(search_results.data.items[0].value.metadata) == 3

    _snapshot(index)
    search_results = index.search("What color are apples?", include_metadata=True)
    assert len(search_results.data.items) == 1
    assert search_results.data.items[0].value.index_source == "snapshot"
    assert search_results.data.items[0].value.value == "Apples are red."
    assert search_results.data.items[0].value.external_id == "TestId"
    assert search_results.data.items[0].value.external_type == "TestType"
    assert len(search_results.data.items[0].value.metadata) == 3

    index.delete()
    steamship = get_steamship_client()

    index = steamship.create_index(plugin_instance=plugin_instance.handle).data

    sentences = []
    for i in range(15):
        sentences.append(f"Orange number {i} is as good as the last")

    sent = "Is orange number 13 Any good?"
    _insert(index, sentences)

    search_results = index.search(sent, include_metadata=True)
    assert len(search_results.data.items) == 1
    assert search_results.data.items[0].value.index_source == "index"
    assert search_results.data.items[0].value.value == "Orange number 13 is as good as the last"
    assert search_results.data.items[0].value.external_id == "TestId"
    assert search_results.data.items[0].value.external_type == "TestType"
    assert len(search_results.data.items[0].value.metadata) == 3

    _snapshot(index, window_size=2)
    search_results = index.search(sent, include_metadata=True)
    assert len(search_results.data.items) == 1
    assert search_results.data.items[0].value.index_source == "snapshot"
    assert search_results.data.items[0].value.value == "Orange number 13 is as good as the last"
    assert search_results.data.items[0].value.external_id == "TestId"
    assert search_results.data.items[0].value.external_type == "TestType"
    assert len(search_results.data.items[0].value.metadata) == 3

    index.delete()
