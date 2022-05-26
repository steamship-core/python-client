import pytest

from steamship import Space, Steamship
from tests.utils.client import get_steamship_client


@pytest.fixture
def client() -> Steamship:
    """
    Returns a client rooted in a new space, then deletes that space afterwards.
    """
    steamship = get_steamship_client()
    space = Space.create(client=steamship).data
    new_client = steamship.for_space(space_id=space.id)
    yield new_client
    space.delete()
