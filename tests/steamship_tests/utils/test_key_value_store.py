from enum import Enum
from typing import Any, Dict, Optional

from steamship_tests.utils.client import get_steamship_client
from steamship_tests.utils.random import random_name

from steamship import Block, File, Space, Steamship, Tag


class KeyValueStore:
    """A simple key value store implemented in Steamship.

    Each entry is stored as an empty file whose "Key" has:
      * Kind = KeyValueStore
      * Name = the key of the (kv) pair
      * Value = a dict set to the value

    This class is stored inside the `tests` folder because:
      1) It has proven useful enough in package development that we wish to make sure it's tested, and
      2) We wish to add KV-functionality to Spaces in general, but
      3) We're not eager to directly add this as a utility class in the codebase.

    For the time being; consider this a copy-paste reference implementation along with tests.
    """

    client: Steamship
    namespace: str

    def __init__(self, client: Steamship, namespace: str = "KeyValueStore"):
        self.client = client
        self.namespace = namespace

    def _get_file(self, or_create: bool = False) -> Optional[File]:
        status_files = File.query(self.client, f'filetag and kind "{self.namespace}"').data.files
        if len(status_files) == 0:
            if not or_create:
                return None
            return File.create(
                self.client,
                blocks=[Block.CreateRequest(text="")],
                tags=[Tag.CreateRequest(kind=self.namespace, name="__init__")],
            ).data
        else:
            return status_files[0]

    def get(self, key: str) -> Optional[Dict]:
        """Gets the value represented by `key`."""
        file = self._get_file()

        if file is None:
            return None

        for tag in file.tags:
            if tag.kind == self.namespace and tag.name == key:
                return tag.value

    def delete(self, key: str) -> bool:
        """Deletes the entry represented by `key`"""
        file = self._get_file()

        if file is None:
            return False

        deleted = False
        for tag in file.tags:
            if tag.kind == self.namespace and tag.name == key:
                tag.delete()

        return deleted

    def set(self, key: str, value: Dict[str, Any]):
        # Sets the entry (key, value)

        # First delete it if it exists to avoid duplicate tags.
        self.delete(key)

        # Now get/create the file
        file = self._get_file(or_create=True)

        req = Tag.CreateRequest(file_id=file.id, kind=self.namespace, name=key, value=value)
        return self.client.post("tag/create", req, expect=Tag)

    def reset(self):
        """Deletes all keys"""
        file = self._get_file()
        if file is not None:
            file.delete()


class SpecializationStatus(str, Enum):
    """These are for use with the"""

    UNSPECIALIZED = "unspecialized"
    SPECIALIZED = "specialized"
    SPECIALIZATION_IN_PROGRESS = "specialization_in_progress"

    @staticmethod
    def from_str(string: str) -> "SpecializationStatus":
        if string == SpecializationStatus.SPECIALIZED.value:
            return SpecializationStatus.SPECIALIZED
        elif string == SpecializationStatus.SPECIALIZATION_IN_PROGRESS.value:
            return SpecializationStatus.SPECIALIZATION_IN_PROGRESS
        return SpecializationStatus.UNSPECIALIZED


def test_key_value_store():
    """We can test the app like a regular python object!"""
    space_handle = random_name()
    client = get_steamship_client(workspace=space_handle)

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

    # Overwite the new one
    kv.set(key2, value_3)
    got = kv.get(key2)
    got_2 = kv.get(key2)
    got_3 = kv.get(key2)

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
    kv.set(key1, {"k": SpecializationStatus.SPECIALIZED.value})
    stat = kv.get(key1)["k"]
    assert isinstance(stat, str)
    stat_enum = SpecializationStatus.from_str(stat)
    assert isinstance(stat_enum, SpecializationStatus)
    assert stat_enum == SpecializationStatus.SPECIALIZED

    # Delete all
    kv.reset()
    assert kv.get(key2) is None

    # Clean up
    Space(client=client, id=client.config.space_id).delete()


def test_kv_namespace_works():
    space_handle = random_name()
    client = get_steamship_client(workspace=space_handle)

    kv1 = KeyValueStore(client=client, namespace="namespace1")
    kv2 = KeyValueStore(client=client, namespace="namespace2")

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
    Space(client=client, id=client.config.space_id).delete()


def test_kv_multi_space_works():
    space_handle = random_name()
    client1 = get_steamship_client(workspace=space_handle)

    space_handle2 = random_name()
    client2 = get_steamship_client(workspace=space_handle2)

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
    Space(client=client1, id=client1.config.space_id).delete()
    Space(client=client2, id=client2.config.space_id).delete()
