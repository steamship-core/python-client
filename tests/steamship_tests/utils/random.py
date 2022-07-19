import contextlib
import random
import string

from steamship import EmbeddingIndex, Space, Steamship


def random_name() -> str:
    letters = string.digits + string.ascii_letters
    return f"test_{''.join(random.choice(letters) for _ in range(10))}"  # noqa: S311


_TEST_EMBEDDER = "test-embedder-v1"


@contextlib.contextmanager
def random_index(steamship: Steamship, plugin_instance: str) -> EmbeddingIndex:
    index = steamship.create_index(plugin_instance=plugin_instance).data
    yield index
    index.delete()  # or whatever you need to do at exit


@contextlib.contextmanager
def temporary_space(steamship: Steamship) -> Space:
    space = Space.create(client=steamship).data
    yield space
    space.delete()  # or whatever you need to do at exit
