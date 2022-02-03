from steamship import App, AppVersion, AppInstance

from ..client.helpers import deploy_app, register_app_as_plugin, _steamship, create_app_zip
from steamship import BlockTypes, File

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_embedder():
    client = _steamship()
    with deploy_app("plugin_embedder.py") as (app, version, instance):
        with register_app_as_plugin(client, "embedder", "embed", app, instance) as plugin:
            e1 = client.embed(["This is a test"], model=plugin.handle)
            assert (e1.error is None)
            assert (len(e1.data.embeddings) == 1)
            assert (len(e1.data.embeddings[0]) > 1)

            e2 = client.embed(["This is a test"], model=plugin.handle)
            assert (e2.error is None)
            assert (len(e2.data.embeddings) == 1)
            assert (len(e2.data.embeddings[0]) == len(e1.data.embeddings[0]))

            e4 = client.embed(["This is a test"], model=plugin.handle)
            assert (e4.error is None)
            assert (len(e4.data.embeddings) == 1)

