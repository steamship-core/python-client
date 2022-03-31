from steamship.base.response import TaskStatus
from steamship.data.embedding_index import IndexSnapshotRequest, IndexSnapshotResponse

from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

_TEST_EMBEDDER = "test-embedder-v1"


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
    index = steamship.create_index(
        name=name,
        plugin=_TEST_EMBEDDER,
        upsert=True
    ).data

    _insert(index, ["Oranges are orange."])
    search_results = index.search("What color are oranges?", includeMetadata=True)
    assert (len(search_results.data.hits) == 1)
    assert (search_results.data.hits[0].indexSource == "index")
    assert (search_results.data.hits[0].value == "Oranges are orange.")
    assert (search_results.data.hits[0].externalId == "TestId")
    assert (search_results.data.hits[0].externalType == "TestType")
    assert (len(search_results.data.hits[0].metadata) == 3)

    _snapshot(index)
    search_results = index.search("What color are oranges?", includeMetadata=True)
    assert (len(search_results.data.hits) == 1)
    assert (search_results.data.hits[0].indexSource == "snapshot")
    assert (search_results.data.hits[0].value == "Oranges are orange.")
    assert (search_results.data.hits[0].externalId == "TestId")
    assert (search_results.data.hits[0].externalType == "TestType")
    assert (len(search_results.data.hits[0].metadata) == 3)

    _insert(index, ["Apples are red."])
    search_results = index.search("What color are apples?", includeMetadata=True)
    assert (len(search_results.data.hits) == 1)
    assert (search_results.data.hits[0].indexSource == "index")
    assert (search_results.data.hits[0].value == "Apples are red.")
    assert (search_results.data.hits[0].externalId == "TestId")
    assert (search_results.data.hits[0].externalType == "TestType")
    assert (len(search_results.data.hits[0].metadata) == 3)

    _snapshot(index)
    search_results = index.search("What color are apples?", includeMetadata=True)
    assert (len(search_results.data.hits) == 1)
    assert (search_results.data.hits[0].indexSource == "snapshot")
    assert (search_results.data.hits[0].value == "Apples are red.")
    assert (search_results.data.hits[0].externalId == "TestId")
    assert (search_results.data.hits[0].externalType == "TestType")
    assert (len(search_results.data.hits[0].metadata) == 3)

    index.delete()
    steamship = _steamship()

    name = _random_name()
    index = steamship.create_index(
        name=name,
        plugin=_TEST_EMBEDDER,
        upsert=True
    ).data

    sentences = []
    for i in range(15):
        sentences.append("Orange number {} is as good as the last".format(i))

    SENT = "Is orange number 13 any good?"
    _insert(index, sentences)

    search_results = index.search(SENT, includeMetadata=True)
    assert (len(search_results.data.hits) == 1)
    assert (search_results.data.hits[0].indexSource == "index")
    assert (search_results.data.hits[0].value == "Orange number 13 is as good as the last")
    assert (search_results.data.hits[0].externalId == "TestId")
    assert (search_results.data.hits[0].externalType == "TestType")
    assert (len(search_results.data.hits[0].metadata) == 3)

    _snapshot(index, windowSize=2)
    search_results = index.search(SENT, includeMetadata=True)
    assert (len(search_results.data.hits) == 1)
    assert (search_results.data.hits[0].indexSource == "snapshot")
    assert (search_results.data.hits[0].value == "Orange number 13 is as good as the last")
    assert (search_results.data.hits[0].externalId == "TestId")
    assert (search_results.data.hits[0].externalType == "TestType")
    assert (len(search_results.data.hits[0].metadata) == 3)

    index.delete()
