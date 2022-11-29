from enum import Enum

import pytest
from steamship_tests.utils.client import get_steamship_client
from steamship_tests.utils.random import random_name

from steamship import Steamship, Workspace
from steamship.utils.kv_store import KeyValueStore


class ExampleEnum(str, Enum):
    VALUE_1 = "value_1"
    VALUE_2 = "value_2"
    VALUE_3 = "value_3"


@pytest.mark.usefixtures("client")
def test_key_value_store(client: Steamship):
    """We can test the app like a regular python object!"""
    client = get_steamship_client()

    kv = KeyValueStore(client=client)
    kv.reset()

    # Getting empty key is None
    assert kv.get("FOO") is None

    key1 = "FOO"
    key2 = "BAR"

    # Set then Get
    value = {"a": 3}
    value_2 = {"hi": "there", "b": 5}
    value_3 = {"j": 9}

    # Set and get
    kv.set(key1, value)
    assert kv.get(key1) == value

    # Get again
    assert kv.get(key1) == value

    # Make a new one
    kv.set(key2, value_2)
    assert kv.get(key2) == value_2
    assert kv.get(key2) != value

    # List all the keys
    res = kv.items()
    assert len(res) == 2
    assert (key1, value) in res
    assert (key2, value_2) in res

    # List just the keys with val1
    res = kv.items(filter_keys=[key1])
    assert len(res) == 1
    assert (key1, value) in res
    assert (key2, value_2) not in res

    # Overwite the new one
    kv.set(key2, value_3)
    got = kv.get(key2)
    got_2 = kv.get(key2)
    got_3 = kv.get(key2)

    # List just the keys with val1
    res = kv.items(filter_keys=[key2])
    assert len(res) == 1
    assert (key1, value) not in res
    assert (key2, value_3) in res

    assert got == value_3
    assert got != value_2
    assert got != value
    assert got == got_2
    assert got == got_3

    # Delete a key
    kv.delete(key1)
    assert kv.get(key1) is None

    # But still others
    assert kv.get(key2) == value_3

    # Test enum
    kv.set(key1, {"k": ExampleEnum.VALUE_2.value})
    stat = kv.get(key1)["k"]
    assert isinstance(stat, str)
    stat_enum = ExampleEnum(stat)
    assert isinstance(stat_enum, ExampleEnum)
    assert stat_enum == ExampleEnum.VALUE_2

    # Delete all
    kv.reset()
    assert kv.get(key2) is None


@pytest.mark.usefixtures("client")
def test_kv_namespace_works(client: Steamship):
    client = get_steamship_client()

    kv1 = KeyValueStore(client=client, store_identifier="namespace1")
    kv2 = KeyValueStore(client=client, store_identifier="namespace2")

    kv1.reset()
    kv2.reset()

    # Getting empty key is None
    key = "key"
    assert kv1.get(key) is None
    assert kv2.get(key) is None

    val1 = {"a": 3}
    val2 = {"a": 4}

    # Set and get
    kv1.set(key, val1)
    assert kv1.get(key) == val1
    assert kv2.get(key) != val1
    assert kv2.get(key) is None

    kv2.set(key, val2)
    assert kv1.get(key) == val1
    assert kv2.get(key) == val2


def test_kv_multi_space_works():
    space_handle = random_name()
    client1 = get_steamship_client(workspace_handle=space_handle)

    space_handle2 = random_name()
    client2 = get_steamship_client(workspace_handle=space_handle2)

    kv1 = KeyValueStore(client=client1)
    kv2 = KeyValueStore(client=client2)

    kv1.reset()
    kv2.reset()

    # Getting empty key is None
    key = "key"
    assert kv1.get(key) is None
    assert kv2.get(key) is None

    val1 = {"a": 3}
    val2 = {"a": 4}

    # Set and get
    kv1.set(key, val1)
    assert kv1.get(key) == val1
    assert kv2.get(key) != val1
    assert kv2.get(key) is None

    kv2.set(key, val2)
    assert kv1.get(key) == val1
    assert kv2.get(key) == val2

    # Clean up
    Workspace(client=client1, id=client1.config.workspace_id).delete()
    Workspace(client=client2, id=client2.config.workspace_id).delete()
