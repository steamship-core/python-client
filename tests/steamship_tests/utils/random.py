import contextlib
import random
import string

from steamship import EmbeddingIndex, Steamship, Workspace


def random_name() -> str:
    """Returns a random name suitable for a handle that has low likelihood of colliding with another.

    Output format matches test_[a-z0-9]+, which should be a valid handle.
    """
    letters = string.digits + string.ascii_letters
    return f"test_{''.join(random.choice(letters) for _ in range(10))}".lower()  # noqa: S311


_TEST_EMBEDDER = "test-embedder-v1"


@contextlib.contextmanager
def random_index(steamship: Steamship, plugin_instance: str) -> EmbeddingIndex:
    index = steamship.use_plugin(
        "embedding-index",
        random_name(),
        config={"embedder": {"plugin_handle": plugin_instance, "fetch_if_exists": True}},
        fetch_if_exists=True,
    )
    yield index
    index.delete()  # or whatever you need to do at exit


@contextlib.contextmanager
def temporary_workspace(steamship: Steamship) -> Workspace:
    workspace = Workspace.create(client=steamship)
    yield workspace
    workspace.delete()  # or whatever you need to do at exit
