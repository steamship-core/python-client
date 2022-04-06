from steamship import App, AppVersion

from tests.client.helpers import _random_name, _steamship, create_app_zip

__copyright__ = "Steamship"
__license__ = "MIT"


def test_version_create():
    client = _steamship()
    name = _random_name()

    app = App.create(client, name=name).data
    zip_bytes = create_app_zip('demo_app.py')

    version = AppVersion.create(
        client,
        appId=app.id,
        filebytes=zip_bytes
    )

    version.wait()

    res = version.data.delete()
    assert (res.error is None)

    res = app.delete()
    assert (res.error is None)
