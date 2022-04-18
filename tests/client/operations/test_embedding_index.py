from steamship.base import Client
from steamship.base.response import TaskStatus
from steamship.data.embeddings import EmbeddedItem
from steamship.data.plugin_instance import PluginInstance

from tests.client.helpers import _random_index, _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

_TEST_EMBEDDER = "test-embedder"


def create_index(client: Client, pluginInstance: str):
    steamship = _steamship()
    name = _random_name()

    # Should require plugin
    task = steamship.create_index(
        name="Test Index"
    )
    assert task.error is not None
    assert task.data is None

    index = steamship.create_index(
        name=name,
        pluginInstance=pluginInstance,
        upsert=True
    ).data
    assert index is not None

    # Duplicate creation should fail with upsert=False
    task = steamship.create_index(
        handle=index.handle,
        pluginInstance=pluginInstance,
        upsert=False
    )
    assert task.error is not None
    assert task.data is None

    index.delete()


def test_create_index():
    steamship = _steamship()
    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    create_index(_steamship(), pluginInstance.handle)


def test_delete_index():
    steamship = _steamship()
    name = _random_name()
    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    index = steamship.create_index(
        name=name,
        pluginInstance=pluginInstance.handle,
        upsert=True
    ).data
    assert (index.id is not None)

    task = steamship.create_index(
        handle=index.handle,
        pluginInstance=pluginInstance.handle,
        upsert=True
    )
    assert task.error is None
    index2 = task.data
    assert (index.id == index2.id)

    index.delete()

    task = steamship.create_index(
        name=name,
        pluginInstance=pluginInstance.handle,
        upsert=True
    )
    assert task.error is None
    assert task.data is not None
    index3 = task.data
    assert (index.id != index3.id)
    index3.delete()


def _list_equal(actual, expected):
    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])


def test_insert_many():
    steamship = _steamship()
    name = _random_name()
    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    with _random_index(steamship, pluginInstance.handle) as index:
        item1 = EmbeddedItem(
            value="Pizza",
            externalId="pizza",
            externalType="food",
            metadata=[1, 2, 3]
        )
        item2 = EmbeddedItem(
            value="Rocket Ship",
            externalId="space",
            externalType="vehicle",
            metadata="Foo"
        )

        index.insert_many([item1, item2])
        index.embed().wait()

        task = index.list_items()
        assert task.error is None
        indexItems = task.data
        assert (len(indexItems.items) == 2)
        assert (len(indexItems.items[0].embedding) > 0)
        assert (len(indexItems.items[1].embedding) > 0)
        assert (len(indexItems.items[0].embedding) == len(indexItems.items[1].embedding))

        res = index.search(item1.value, includeMetadata=True, k=100)
        assert (res.data.items is not None)
        assert (len(res.data.items) == 2)
        assert (res.data.items[0].value.value == item1.value)
        assert (res.data.items[0].value.externalId == item1.externalId)
        assert (res.data.items[0].value.externalType == item1.externalType)
        _list_equal(res.data.items[0].value.metadata, item1.metadata)

        res = index.search(item2.value, includeMetadata=True)
        assert (res.data.items is not None)
        assert (res.data.items[0].value.value == item2.value)
        assert (res.data.items[0].value.externalId == item2.externalId)
        assert (res.data.items[0].value.externalType == item2.externalType)
        assert (res.data.items[0].value.metadata == item2.metadata)


def test_embed_task():
    steamship = _steamship()
    name = _random_name()
    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    with _random_index(steamship, pluginInstance.handle) as index:
        insert_results = index.insert("test", reindex=False)
        res = index.embed()

        assert (res.task.taskId is not None)
        assert (res.task.state is not None)
        assert (res.task.taskCreatedOn is not None)
        assert (res.task.taskLastModifiedOn is not None)
        assert (res.task.state == TaskStatus.waiting)
        res.wait()
        assert (res.task.state == TaskStatus.succeeded)


def test_duplicate_inserts():
    steamship = _steamship()
    name = _random_name()

    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    with _random_index(steamship, pluginInstance.handle) as index:
        # Test for suppressed re-indexing
        A1 = "Ted can eat an entire block of cheese."
        Q1 = "Who can eat the most cheese"
        insert_results = index.insert(A1)
        search_results = index.search(Q1)


def test_index_usage():
    steamship = _steamship()
    name = _random_name()

    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    with _random_index(steamship, pluginInstance.handle) as index:
        A1 = "Ted can eat an entire block of cheese."
        Q1 = "Who can eat the most cheese"
        insert_results = index.insert(A1)
        search_results = index.search(Q1)

        # Now embed
        task = index.embed()
        task.wait()
        task.check()
        assert (task.task.state == TaskStatus.succeeded)

        search_results = index.search(Q1)
        assert (len(search_results.data.items) == 1)
        assert (search_results.data.items[0].value.value == A1)

        # Associate metadata
        A2 = "Armadillo shells are bulletproof."
        Q2 = "What is something interesting about Armadillos?"
        A2id = "A2id"
        A2type = "A2type"
        A2metadata = dict(
            id=A2id,
            idid="{}{}".format(A2id, A2id),
            boolVal=True,
            intVal=123,
            floatVal=1.2
        )

        insert_results2 = index.insert(
            A2,
            externalId=A2id,
            externalType=A2type,
            metadata=A2metadata
        )
        search_results2 = index.search(Q2)
        assert (len(search_results2.data.items) == 1)
        assert (search_results2.data.items[0].value.value == A2)
        assert (search_results2.data.items[0].value.externalId == None)
        assert (search_results2.data.items[0].value.externalType == None)
        assert (search_results2.data.items[0].value.metadata == None)

        search_results3 = index.search(Q2, includeMetadata=True)
        assert (len(search_results3.data.items) == 1)
        assert (search_results3.data.items[0].value.value == A2)
        assert (search_results3.data.items[0].value.externalId == A2id)
        assert (search_results3.data.items[0].value.externalType == A2type)

        assert (search_results3.data.items[0].value.metadata == A2metadata)
        # Because I don't know pytest enough to fully trust the dict comparison..
        assert (search_results3.data.items[0].value.metadata["id"] == A2id)
        assert (search_results3.data.items[0].value.metadata["idid"] == "{}{}".format(A2id, A2id))

        search_results4 = index.search(Q2, k=10)
        assert (len(search_results4.data.items) == 2)
        assert (search_results4.data.items[0].value.value == A2)
        assert (search_results4.data.items[1].value.value == A1)


def test_multiple_queries():
    steamship = _steamship()
    name = _random_name()

    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    with _random_index(steamship, pluginInstance.handle) as index:
        # Test for suppressed re-indexing
        A1 = "Ted can eat an entire block of cheese."
        A2 = "Joe can drink an entire glass of water."
        insert_results = index.insert_many([A1, A2])
        index.embed().wait()

        QS1 = ["Who can eat the most cheese", "Who can run the fastest?"]
        search_results = index.search(QS1)
        assert (len(search_results.data.items) == 1)
        assert (search_results.data.items[0].value.value == A1)
        assert (search_results.data.items[0].value.query == QS1[0])

        QS2 = ["Who can tie a shoe?", "Who can drink the most water?"]
        search_results = index.search(QS2)
        assert (len(search_results.data.items) == 1)
        assert (search_results.data.items[0].value.value == A2)
        assert (search_results.data.items[0].value.query == QS2[1])

        QS3 = ["What can Ted do?", "What can Sam do?", "What can Jerry do?"]
        search_results = index.search(QS3)
        assert (len(search_results.data.items) == 1)
        assert (search_results.data.items[0].value.value == A1)
        assert (search_results.data.items[0].value.query == QS3[0])

        QS3 = ["What can Sam do?", "What can Ted do?", "What can Jerry do?"]
        search_results = index.search(QS3)
        assert (len(search_results.data.items) == 1)
        assert (search_results.data.items[0].value.value == A1)
        assert (search_results.data.items[0].value.query == QS3[1])

        index.create_snapshot().wait()

        A3 = "Susan can run very fast."
        A4 = "Brenda can fight alligators."
        insert_results = index.insert_many([A3, A4])
        index.embed().wait()

        QS4 = ["What can Brenda do?", "What can Ronaldo do?", "What can Jerry do?"]
        search_results = index.search(QS4)
        assert (len(search_results.data.items) == 1)
        assert (search_results.data.items[0].value.value == A4)
        assert (search_results.data.items[0].value.query == QS4[0])

        QS4 = ["What can Brenda do?", "Who should run a marathon?", "What can Jerry do?"]
        search_results = index.search(QS4, k=2)
        assert (len(search_results.data.items) == 2)
        assert (search_results.data.items[0].value.value == A4)
        assert (search_results.data.items[0].value.query == QS4[0])
        assert (search_results.data.items[1].value.value == A3)
        assert (search_results.data.items[1].value.query == QS4[1])


def test_empty_queries():
    steamship = _steamship()
    name = _random_name()

    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    with _random_index(steamship, pluginInstance.handle) as index:
        A1 = "Ted can eat an entire block of cheese."
        A2 = "Joe can drink an entire glass of water."
        insert_results = index.insert_many([A1, A2])
        index.embed().wait()

        search_results = index.search(None)
        assert (search_results.error is not None)
        assert (search_results.data is None)

        # These technically don't count as empty. Leaving this test in here
        # to encode and capture that in case we want to change it.
        search_results = index.search([])
        assert (len(search_results.data.items) == 0)

        search_results = index.search("")
        assert (len(search_results.data.items) == 1)
