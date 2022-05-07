from steamship import App

from tests.client.helpers import _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_app_create():
    client = _steamship()

    app = App.create(client)
    assert (app.error is None)
    assert (app.data is not None)

    res = app.data.delete()
    assert (app.error is None)
