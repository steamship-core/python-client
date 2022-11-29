import pytest
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_index, random_name

from steamship import SteamshipError, Tag

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
        item1 = Tag(text="Pizza", name="pizza", kind="food", value={"nums": [1, 2, 3]})
        item2 = Tag(
            text="Rocket Ship",
            name="workspace",
            kind="vehicle",
            value={"name": "Foo"},
        )

        index.insert([item1, item2])

        res = index.search(item1.text, k=100)
        res.wait()
        items = res.output.items
        assert items is not None
        assert len(items) == 2
        item0: Tag = items[0].tag
        assert item0.text == item1.text
        assert item0.name == item1.name
        assert item0.kind == item1.kind
        _list_equal(item0.value.get("nums"), item1.value.get("nums"))

        res = index.search(item2.text)
        res.wait()
        items = res.output.items
        assert items is not None
        item0: Tag = items[0].tag
        assert item0.text == item2.text
        assert item0.name == item2.name
        assert item0.kind == item2.kind
        assert item0.value.get("name") == item2.value.get("name")
        assert "_file_id" not in item0.value
        assert "_tag_id" not in item0.value
        assert "_block_id" not in item0.value


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
        assert search_results[0].tag.text == a1
        assert search_results[0].tag.name is None
        assert search_results[0].tag.kind is None
        assert len(search_results[0].tag.value) == 0

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
        tag0: Tag = search_results[0].tag
        assert tag0.text == a2
        assert tag0.name == a2id
        assert tag0.kind == a2type
        assert tag0.value == a2metadata

        search_results4 = index.search(q2, k=10)
        search_results4.wait()
        search_results = search_results4.output.items
        assert len(search_results) == 2
        assert search_results[0].tag.text == a2
        assert search_results[1].tag.text == a1


def test_empty_queries():
    steamship = get_steamship_client()
    with random_index(steamship, _TEST_EMBEDDER) as index:
        a1 = "Ted can eat an entire block of cheese."
        a2 = "Joe can drink an entire glass of water."
        _ = index.insert([Tag(text=a1), Tag(text=a2)])

        with pytest.raises(SteamshipError):
            _ = index.search(None)

        with pytest.raises(SteamshipError):
            index.search("")

        with pytest.raises(SteamshipError):
            index.search("  ")
