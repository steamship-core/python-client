from steamship import App

from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_app_create():
    client = _steamship()
    name = _random_name()

    app = App.create(client, name=name)
    assert (app.error is None)
    assert (app.data is not None)
    assert (app.data.name == name)

    res = app.data.delete()
    assert (app.error is None)
