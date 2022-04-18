from steamship import PluginInstance
from steamship.base.response import TaskStatus
from steamship.data.embeddings import IndexSnapshotRequest, IndexSnapshotResponse

from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

_TEST_EMBEDDER = "test-embedder"


def _insert(index, items):
    for item in items:
        index.insert(item, "TestId", "TestType", [1, 2, 3])

    # Now embed
    task = index.embed()
    task.wait()
    task.check()
    assert (task.task.state == TaskStatus.succeeded)


def _snapshot(index, windowSize=None):
    if windowSize is None:
        task = index.create_snapshot()
        task.wait()
        task.check()
    else:
        # We do this manually so as not to clutter the end-user visible
        # API with debug/testing parameters
        req = IndexSnapshotRequest(
            index.id,
            windowSize=windowSize
        )
        task = index.client.post(
            'embedding-index/snapshot/create',
            req,
            expect=IndexSnapshotResponse,
            asynchronous=True
        )
        task.wait()
        task.check()


def test_snapshot_create():
    steamship = _steamship()

    name = _random_name()
    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    index = steamship.create_index(
        name=name,
        pluginInstance=pluginInstance.handle,
        upsert=True
    ).data

    _insert(index, ["Oranges are orange."])
    search_results = index.search("What color are oranges?", includeMetadata=True)
    assert (len(search_results.data.items) == 1)
    assert (search_results.data.items[0].value.indexSource == "index")
    assert (search_results.data.items[0].value.value == "Oranges are orange.")
    assert (search_results.data.items[0].value.externalId == "TestId")
    assert (search_results.data.items[0].value.externalType == "TestType")
    assert (len(search_results.data.items[0].value.metadata) == 3)

    _snapshot(index)
    search_results = index.search("What color are oranges?", includeMetadata=True)
    assert (len(search_results.data.items) == 1)
    assert (search_results.data.items[0].value.indexSource == "snapshot")
    assert (search_results.data.items[0].value.value == "Oranges are orange.")
    assert (search_results.data.items[0].value.externalId == "TestId")
    assert (search_results.data.items[0].value.externalType == "TestType")
    assert (len(search_results.data.items[0].value.metadata) == 3)

    _insert(index, ["Apples are red."])
    search_results = index.search("What color are apples?", includeMetadata=True)
    assert (len(search_results.data.items) == 1)
    assert (search_results.data.items[0].value.indexSource == "index")
    assert (search_results.data.items[0].value.value == "Apples are red.")
    assert (search_results.data.items[0].value.externalId == "TestId")
    assert (search_results.data.items[0].value.externalType == "TestType")
    assert (len(search_results.data.items[0].value.metadata) == 3)

    _snapshot(index)
    search_results = index.search("What color are apples?", includeMetadata=True)
    assert (len(search_results.data.items) == 1)
    assert (search_results.data.items[0].value.indexSource == "snapshot")
    assert (search_results.data.items[0].value.value == "Apples are red.")
    assert (search_results.data.items[0].value.externalId == "TestId")
    assert (search_results.data.items[0].value.externalType == "TestType")
    assert (len(search_results.data.items[0].value.metadata) == 3)

    index.delete()
    steamship = _steamship()

    name = _random_name()
    index = steamship.create_index(
        name=name,
        pluginInstance=pluginInstance.handle,
        upsert=True
    ).data

    sentences = []
    for i in range(15):
        sentences.append("Orange number {} is as good as the last".format(i))

    SENT = "Is orange number 13 any good?"
    _insert(index, sentences)

    search_results = index.search(SENT, includeMetadata=True)
    assert (len(search_results.data.items) == 1)
    assert (search_results.data.items[0].value.indexSource == "index")
    assert (search_results.data.items[0].value.value == "Orange number 13 is as good as the last")
    assert (search_results.data.items[0].value.externalId == "TestId")
    assert (search_results.data.items[0].value.externalType == "TestType")
    assert (len(search_results.data.items[0].value.metadata) == 3)

    _snapshot(index, windowSize=2)
    search_results = index.search(SENT, includeMetadata=True)
    assert (len(search_results.data.items) == 1)
    assert (search_results.data.items[0].value.indexSource == "snapshot")
    assert (search_results.data.items[0].value.value == "Orange number 13 is as good as the last")
    assert (search_results.data.items[0].value.externalId == "TestId")
    assert (search_results.data.items[0].value.externalType == "TestType")
    assert (len(search_results.data.items[0].value.metadata) == 3)

    index.delete()
