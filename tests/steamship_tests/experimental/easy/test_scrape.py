import pytest

from steamship import Steamship
from steamship.experimental.easy import scrape


@pytest.mark.usefixtures("client")
def test_import_wikipedia(client: Steamship):
    file = scrape(client, "https://en.wikipedia.org/wiki/Steamship")
    assert file.id is not None
    content = file.raw().decode("utf-8")
    assert "Steamship" in content
    file.delete()


# @pytest.mark.usefixtures("client")
# def test_import_youtube(client: Steamship):
#     file = scrape(client, "https://www.youtube.com/watch?v=LXDZ6aBjv_I")
#     assert file.id is not None
#     content = file.raw()
#     assert content is not None
#     file.delete()
