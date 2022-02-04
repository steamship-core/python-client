import contextlib
import io
import os
import random
import string
import zipfile

from steamship import App, AppVersion, AppInstance
from steamship import Steamship, EmbeddingIndex, File
from steamship.base import Client
from steamship.data.plugin import Plugin
from steamship.data.user import User

__copyright__ = "Steamship"
__license__ = "MIT"


def _env_or(env_var: str, or_val: str) -> str:
    if env_var in os.environ:
        return os.getenv(env_var)
    return or_val


def _random_name() -> str:
    letters = string.digits + string.ascii_letters
    id = ''.join(random.choice(letters) for i in range(10))
    return "test_{}".format(id)


_TEST_EMBEDDER = "test-embedder-v1"


@contextlib.contextmanager
def _random_index(steamship: Steamship, model: str = _TEST_EMBEDDER) -> EmbeddingIndex:
    index = steamship.create_index(
        model=model
    ).data
    yield index
    index.delete()  # or whatever you need to do at exit


@contextlib.contextmanager
def _random_file(steamship: Steamship, content: str = "") -> File:
    file = steamship.create_file(
        name=_random_name(),
        contents=content
    ).data
    yield file
    file.delete()  # or whatever you need to do at exit


def _steamship() -> Steamship:
    # This should automatically pick up variables from the environment.
    return Steamship(profile="test")


def create_app_zip(filename) -> bytes:
    full_path = os.path.join(os.path.dirname(__file__), '..', 'demo_apps', filename)
    zip_buffer = io.BytesIO()

    files = []
    files.append(('api.py', io.BytesIO(open(full_path, 'rb').read())))

    # TODO: This is very dependent on the setup of the local machine.
    # Might be good to find a more machine-invariant solution here.
    # The goal is to copy in all the dependencies of the lambda package.
    # Which are: steamship (current repo), setuptools_scm, requests
    venv = os.path.join(os.path.dirname(__file__), '..', '..', '.venv', 'lib', 'python3.8', 'site-packages')

    pypi_zips = [
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'steamship'),
        os.path.join(venv, 'setuptools_scm'),
        os.path.join(venv, 'requests'),
    ]

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in files:
            zip_file.writestr(file_name, data.getvalue())

        for pypi_zip in pypi_zips:
            for root, dirs, files in os.walk(pypi_zip):
                for file in files:
                    zip_file.write(
                        os.path.join(root, file),
                        os.path.relpath(
                            os.path.join(root, file),
                            os.path.join(pypi_zip, '..')
                        )
                    )

    ret = zip_buffer.getvalue()

    with open("/tmp/foo.zip", "wb") as f:  # use `wb` mode
        f.write(ret)

    return ret


@contextlib.contextmanager
def deploy_app(py_name: str):
    client = _steamship()
    name = _random_name()
    app = App.create(client, name=name)
    assert (app.error is None)
    assert (app.data is not None)
    app = app.data

    zip_bytes = create_app_zip(py_name)
    version = AppVersion.create(
        client,
        appId=app.id,
        filebytes=zip_bytes
    )
    version.wait()
    assert (version.error is None)
    assert (version.data is not None)
    version = version.data

    instance = AppInstance.create(
        client,
        appId=app.id,
        appVersionId=version.id,
    )
    instance.wait()
    assert (instance.error is None)
    assert (instance.data is not None)
    instance = instance.data

    assert (instance.appId == app.id)
    assert (instance.appVersionId == version.id)

    user = User.current(client).data

    assert (instance.userHandle == user.handle)
    assert (instance.userId == user.id)

    yield (app, version, instance)

    res = instance.delete()
    assert (res.error is None)

    res = version.delete()
    assert (res.error is None)

    res = app.delete()
    assert (res.error is None)


@contextlib.contextmanager
def register_app_as_plugin(client: Client, type: string, path: str, app: App, instance: AppInstance) -> Plugin:
    url = instance.full_url_for(
        path=path,
        appHandle=app.handle,
        useSubdomain=False  # In a test setting, the subdomain is hard to use
    )
    metadata = dict(
        http=dict(
            headers=dict(
                Authorization="Bearer {}".format(client.config.apiKey)
            )
        )
    )

    plugin = Plugin.create(
        client=client,
        name=instance.name,
        handle=instance.handle,
        description="Auto-generated",
        modelType=type,
        url=url,
        adapterType="jsonOverHttp",
        isPublic=True,
        metadata=metadata
    )
    assert (plugin.error is None)
    assert (plugin.data is not None)
    plugin = plugin.data

    yield plugin

    res = plugin.delete()
    assert (res.error is None)
