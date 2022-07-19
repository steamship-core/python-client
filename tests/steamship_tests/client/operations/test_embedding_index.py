from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_index

from steamship.base import Client
from steamship.base.response import TaskState
from steamship.data.embeddings import EmbeddedItem
from steamship.data.plugin_instance import PluginInstance

_TEST_EMBEDDER = "test-embedder"


def create_index(_: Client, plugin_instance: str):
    steamship = get_steamship_client()

    # Should require plugin
    task = steamship.create_index()
    assert task.error is not None

    index = steamship.create_index(plugin_instance=plugin_instance).data
    assert index is not None

    # Duplicate creation should fail with upsert=False
    task = steamship.create_index(
        handle=index.handle, plugin_instance=plugin_instance, upsert=False
    )
    assert task.error is not None

    index.delete()


def test_create_index():
    client = get_steamship_client()
    plugin_instance = PluginInstance.create(client, plugin_handle=_TEST_EMBEDDER).data
    create_index(client, plugin_instance.handle)


def test_delete_index():
    steamship = get_steamship_client()
    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER).data
    index = steamship.create_index(plugin_instance=plugin_instance.handle).data
    assert index.id is not None

    task = steamship.create_index(handle=index.handle, plugin_instance=plugin_instance.handle)
    assert task.error is None
    index2 = task.data
    assert index.id == index2.id

    index.delete()

    task = steamship.create_index(plugin_instance=plugin_instance.handle)
    assert task.error is None
    assert task.data is not None
    index3 = task.data
    assert index.id != index3.id
    index3.delete()


def _list_equal(actual, expected):
    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])


def test_insert_many():
    steamship = get_steamship_client()
    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER).data
    with random_index(steamship, plugin_instance.handle) as index:
        item1 = EmbeddedItem(
            value="Pizza", external_id="pizza", external_type="food", metadata=[1, 2, 3]
        )
        item2 = EmbeddedItem(
            value="Rocket Ship",
            external_id="space",
            external_type="vehicle",
            metadata="Foo",
        )

        index.insert_many([item1, item2])
        index.embed().wait()

        task = index.list_items()
        assert task.error is None
        index_items = task.data
        assert len(index_items.items) == 2
        assert len(index_items.items[0].embedding) > 0
        assert len(index_items.items[1].embedding) > 0
        assert len(index_items.items[0].embedding) == len(index_items.items[1].embedding)

        res = index.search(item1.value, include_metadata=True, k=100)
        assert res.data.items is not None
        assert len(res.data.items) == 2
        assert res.data.items[0].value.value == item1.value
        assert res.data.items[0].value.external_id == item1.external_id
        assert res.data.items[0].value.external_type == item1.external_type
        _list_equal(res.data.items[0].value.metadata, item1.metadata)

        res = index.search(item2.value, include_metadata=True)
        assert res.data.items is not None
        assert res.data.items[0].value.value == item2.value
        assert res.data.items[0].value.external_id == item2.external_id
        assert res.data.items[0].value.external_type == item2.external_type
        assert res.data.items[0].value.metadata == item2.metadata


def test_embed_task():
    steamship = get_steamship_client()
    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER).data
    with random_index(steamship, plugin_instance.handle) as index:
        _ = index.insert("test", reindex=False)
        res = index.embed()

        assert res.task.task_id is not None
        assert res.task.state is not None
        assert res.task.task_created_on is not None
        assert res.task.task_last_modified_on is not None
        assert res.task.state == TaskState.waiting
        res.wait()
        assert res.task.state == TaskState.succeeded


def test_duplicate_inserts():
    steamship = get_steamship_client()

    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER).data
    with random_index(steamship, plugin_instance.handle) as index:
        # Test for suppressed re-indexing
        a1 = "Ted can eat an entire block of cheese."
        q1 = "Who can eat the most cheese"
        _ = index.insert(a1)
        _ = index.search(q1)


def test_index_usage():
    steamship = get_steamship_client()

    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER).data
    with random_index(steamship, plugin_instance.handle) as index:
        a1 = "Ted can eat an entire block of cheese."
        q1 = "Who can eat the most cheese"
        _ = index.insert(a1)
        _ = index.search(q1)

        # Now embed
        task = index.embed()
        task.wait()
        task.refresh()
        assert task.task.state == TaskState.succeeded

        search_results = index.search(q1)
        assert len(search_results.data.items) == 1
        assert search_results.data.items[0].value.value == a1

        # Associate metadata
        a2 = "Armadillo shells are bulletproof."
        q2 = "What is something interesting about Armadillos?"
        a2id = "A2id"
        a2type = "A2type"
        a2metadata = {
            "id": a2id,
            "idid": f"{a2id}{a2id}",
            "boolVal": True,
            "intVal": 123,
            "floatVal": 1.2,
        }

        _ = index.insert(a2, external_id=a2id, external_type=a2type, metadata=a2metadata)
        search_results2 = index.search(q2)
        assert len(search_results2.data.items) == 1
        assert search_results2.data.items[0].value.value == a2
        assert search_results2.data.items[0].value.external_id is None
        assert search_results2.data.items[0].value.external_type is None
        assert search_results2.data.items[0].value.metadata is None

        search_results3 = index.search(q2, include_metadata=True)
        assert len(search_results3.data.items) == 1
        assert search_results3.data.items[0].value.value == a2
        assert search_results3.data.items[0].value.external_id == a2id
        assert search_results3.data.items[0].value.external_type == a2type

        assert search_results3.data.items[0].value.metadata == a2metadata
        # Because I don't know pytest enough to fully trust the dict comparison..
        assert search_results3.data.items[0].value.metadata["id"] == a2id
        assert search_results3.data.items[0].value.metadata["idid"] == f"{a2id}{a2id}"

        search_results4 = index.search(q2, k=10)
        assert len(search_results4.data.items) == 2
        assert search_results4.data.items[0].value.value == a2
        assert search_results4.data.items[1].value.value == a1


def test_multiple_queries():
    steamship = get_steamship_client()

    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER).data
    with random_index(steamship, plugin_instance.handle) as index:
        # Test for suppressed re-indexing
        a1 = "Ted can eat an entire block of cheese."
        a2 = "Joe can drink an entire glass of water."
        _ = index.insert_many([a1, a2])
        index.embed().wait()

        qs1 = ["Who can eat the most cheese", "Who can run the fastest?"]
        search_results = index.search(qs1)
        assert len(search_results.data.items) == 1
        assert search_results.data.items[0].value.value == a1
        assert search_results.data.items[0].value.query == qs1[0]

        qs2 = ["Who can tie a shoe?", "Who can drink the most water?"]
        search_results = index.search(qs2)
        assert len(search_results.data.items) == 1
        assert search_results.data.items[0].value.value == a2
        assert search_results.data.items[0].value.query == qs2[1]

        qs3 = ["What can Ted do?", "What can Sam do?", "What can Jerry do?"]
        search_results = index.search(qs3)
        assert len(search_results.data.items) == 1
        assert search_results.data.items[0].value.value == a1
        assert search_results.data.items[0].value.query == qs3[0]

        qs3 = ["What can Sam do?", "What can Ted do?", "What can Jerry do?"]
        search_results = index.search(qs3)
        assert len(search_results.data.items) == 1
        assert search_results.data.items[0].value.value == a1
        assert search_results.data.items[0].value.query == qs3[1]

        index.create_snapshot().wait()

        a3 = "Susan can run very fast."
        a4 = "Brenda can fight alligators."
        _ = index.insert_many([a3, a4])
        index.embed().wait()

        qs4 = ["What can Brenda do?", "What can Ronaldo do?", "What can Jerry do?"]
        search_results = index.search(qs4)
        assert len(search_results.data.items) == 1
        assert search_results.data.items[0].value.value == a4
        assert search_results.data.items[0].value.query == qs4[0]

        qs4 = [
            "What can Brenda do?",
            "Who should run a marathon?",
            "What can Jerry do?",
        ]
        search_results = index.search(qs4, k=2)
        assert len(search_results.data.items) == 2
        assert search_results.data.items[0].value.value == a4
        assert search_results.data.items[0].value.query == qs4[0]
        assert search_results.data.items[1].value.value == a3
        assert search_results.data.items[1].value.query == qs4[1]


def test_empty_queries():
    steamship = get_steamship_client()

    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER).data
    with random_index(steamship, plugin_instance.handle) as index:
        a1 = "Ted can eat an entire block of cheese."
        a2 = "Joe can drink an entire glass of water."
        _ = index.insert_many([a1, a2])
        index.embed().wait()

        search_results = index.search(None)
        assert search_results.error is not None

        # These technically don't count as empty. Leaving this test in here
        # to encode and capture that in case we want to change it.
        search_results = index.search([])
        # noinspection PyUnresolvedReferences
        assert len(search_results.data.items) == 0

        search_results = index.search("")
        # noinspection PyUnresolvedReferences
        assert len(search_results.data.items) == 1
