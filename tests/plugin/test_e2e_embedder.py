from ..client.helpers import deploy_app, register_app_as_plugin, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

from tests.client.operations.test_embed import basic_embeddings, basic_embedding_search
from tests.client.operations.test_embedding_index import create_index


def test_e2e_embedder():
    client = _steamship()
    with deploy_app("plugin_embedder.py") as (app, version, instance):
        with register_app_as_plugin(client, "embedder", "embed", app, instance) as plugin:
            e1 = client.embed(["This is a test"], plugin=plugin.handle)
            assert (e1.error is None)
            assert (len(e1.data.embeddings) == 1)
            assert (len(e1.data.embeddings[0]) > 1)

            e2 = client.embed(["This is a test"], plugin=plugin.handle)
            assert (e2.error is None)
            assert (len(e2.data.embeddings) == 1)
            assert (len(e2.data.embeddings[0]) == len(e1.data.embeddings[0]))

            e4 = client.embed(["This is a test"], plugin=plugin.handle)
            assert (e4.error is None)
            assert (len(e4.data.embeddings) == 1)

            # Now lets run all the other embedding tests
            basic_embeddings(client, plugin.handle)
            basic_embedding_search(client, plugin.handle)

            create_index(client, plugin.handle)
