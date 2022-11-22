import pytest
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_index, random_name

from steamship import SteamshipError, Tag
from steamship.data.embeddings import EmbeddedItem

_TEST_EMBEDDER = "test-embedder"


def test_create_index():
    client = get_steamship_client()

    index_handle = random_name()
    index = client.use_plugin(
        "embedding-index",
        index_handle,
        config={"embedder": {"plugin_handle": _TEST_EMBEDDER, "fetch_if_exists": True}},
        fetch_if_exists=False,
    )

    assert index is not None

    # Duplicate creation should fail with fetch_if_exists=False
    with pytest.raises(SteamshipError):
        index = client.use_plugin(
            "embedding-index",
            index_handle,
            config={"embedder": {"plugin_handle": _TEST_EMBEDDER, "fetch_if_exists": True}},
            fetch_if_exists=False,
        )

    # Duplicate creation should fail with fetch_if_exists=False for embedder
    with pytest.raises(SteamshipError):
        index = client.use_plugin(
            "embedding-index",
            index_handle,
            config={"embedder": {"plugin_handle": _TEST_EMBEDDER, "fetch_if_exists": False}},
            fetch_if_exists=True,
        )

    index.delete()


def test_reload_and_delete_index():
    steamship = get_steamship_client()
    index = steamship.use_plugin(
        "embedding-index",
        random_name(),
        config={"embedder": {"plugin_handle": _TEST_EMBEDDER, "fetch_if_exists": True}},
        fetch_if_exists=True,
    )
    assert index.id is not None

    index2 = steamship.use_plugin(
        "embedding-index",
        index.handle,
        config={"embedder": {"plugin_handle": _TEST_EMBEDDER, "fetch_if_exists": True}},
        fetch_if_exists=True,
    )

    assert index.id == index2.id
    index.delete()

    # Having deleted it, the ID should now be different
    index3 = steamship.use_plugin(
        "embedding-index",
        index.handle,
        config={"embedder": {"plugin_handle": _TEST_EMBEDDER, "fetch_if_exists": True}},
        fetch_if_exists=True,
    )
    assert index.id != index3.id
    index3.delete()


def _list_equal(actual, expected):
    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])


def test_insert_many():
    steamship = get_steamship_client()
    with random_index(steamship, _TEST_EMBEDDER) as index:
        item1 = EmbeddedItem(text="Pizza", name="pizza", kind="food", value=[1, 2, 3])
        item2 = Tag(
            text="Rocket Ship",
            name="workspace",
            kind="vehicle",
            value="Foo",
        )

        index.insert([item1, item2])

        # TODO(ted): Do we want to continue supporting the `list` operation on index?
        # list_response = index.index.list_items()
        # assert len(list_response.items) == 2
        # assert len(list_response.items[0].embedding) > 0
        # assert len(list_response.items[1].embedding) > 0
        # assert len(list_response.items[0].embedding) == len(list_response.items[1].embedding)

        res = index.search(item1.value, k=100)
        res.wait()
        items = res.output.items
        assert items is not None
        assert len(items) == 2
        item0: Tag = items[0].value
        assert item0.text == item1.text
        assert item0.name == item1.name
        assert item0.kind == item1.kind
        _list_equal(item0.value, item1.value)

        res = index.search(item2.value)
        res.wait()
        items = res.output.items
        assert items is not None
        item0: Tag = items[0]
        assert item0.text == item2.text
        assert item0.name == item2.name
        assert item0.kind == item2.kind
        assert item0.value == item2.value


# TODO(ted) - Find a way to bring this test back after the rewrite is complete.
#             For now, since some of these operations become synchronous, it's hard to test the tasking.
# def test_embed_task():
#     steamship = get_steamship_client()
#     with random_index(steamship, _TEST_EMBEDDER) as index:
#         _ = index.insert(Tag(text="test"))
#         res = index.index.embed()
#
#         assert res.task_id is not None
#         assert res.state is not None
#         assert res.task_created_on is not None
#         assert res.task_last_modified_on is not None
#         assert res.state == TaskState.waiting
#         res.wait()
#         assert res.state == TaskState.succeeded


def test_duplicate_inserts():
    steamship = get_steamship_client()
    with random_index(steamship, _TEST_EMBEDDER) as index:
        # Test for suppressed re-indexing
        a1 = "Ted can eat an entire block of cheese."
        q1 = "Who can eat the most cheese"
        _ = index.insert(Tag(text=a1))
        _ = index.search(q1)


def test_index_usage():
    steamship = get_steamship_client()
    with random_index(steamship, _TEST_EMBEDDER) as index:
        a1 = "Ted can eat an entire block of cheese."
        q1 = "Who can eat the most cheese"
        _ = index.insert(Tag(text=a1))

        search_results = index.search(q1)
        search_results.wait()
        search_results = search_results.output.items
        assert len(search_results) == 1
        assert search_results[0].value.text == a1

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

        _ = index.insert(Tag(text=a2, name=a2id, kind=a2type, value=a2metadata))
        search_results2 = index.search(q2)
        search_results2.wait()
        search_results = search_results2.output.items
        assert len(search_results) == 1
        tag0: Tag = search_results[0].value
        assert tag0.text == a2
        assert tag0.name is None
        assert tag0.kind is None
        assert tag0.value is None

        search_results3 = index.search(q2)
        search_results3.wait()
        search_results = search_results3.output.items
        assert len(search_results) == 1
        tag0: Tag = search_results[0].value
        assert tag0.text == a2
        assert tag0.name == a2id
        assert tag0.kind == a2type
        assert tag0.value == a2metadata
        assert tag0.value["id"] == a2id
        assert tag0.value["idid"] == f"{a2id}{a2id}"

        search_results4 = index.search(q2, k=10)
        search_results4.wait()
        search_results = search_results4.output.items
        assert len(search_results) == 2
        assert search_results[0].value.text == a2
        assert search_results[1].value.text == a1


def test_empty_queries():
    steamship = get_steamship_client()
    with random_index(steamship, _TEST_EMBEDDER) as index:
        a1 = "Ted can eat an entire block of cheese."
        a2 = "Joe can drink an entire glass of water."
        _ = index.insert_many([Tag(text=a1), Tag(text=a2)])

        with pytest.raises(SteamshipError):
            _ = index.search(None)

        search_results = index.search("")

        search_results.wait()
        search_results = search_results.output
        # noinspection PyUnresolvedReferences
        assert len(search_results.items) == 1
