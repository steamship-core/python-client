from steamship import App

__copyright__ = "Steamship"
__license__ = "MIT"

from tests.utils.client import get_steamship_client


def test_app_create():
    client = get_steamship_client()

    app = App.create(client)
    assert app.error is None
    assert app.data is not None

    res = app.data.delete()
    assert app.error is None
