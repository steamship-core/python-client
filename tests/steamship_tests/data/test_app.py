from steamship_tests.utils.fixtures import get_steamship_client

from steamship import App


def test_app_create():
    client = get_steamship_client()

    app = App.create(client)
    assert app.error is None
    assert app.data is not None

    _ = app.data.delete()
    assert app.error is None
