from steamship.data.plugin import PluginType
from tests import PLUGINS_PATH
from tests.tests.client.operations.test_embed import (
    basic_embedding_search,
    basic_embeddings,
    count_embeddings,
)
from tests.tests.client.operations.test_embedding_index import create_index
from tests.utils.deployables import deploy_plugin
from tests.utils.fixtures import get_steamship_client


def test_e2e_embedder():
    client = get_steamship_client()
    embedder_path = PLUGINS_PATH / "taggers" / "plugin_embedder.py"

    with deploy_plugin(client, embedder_path, PluginType.tagger) as (
        plugin,
        version,
        instance,
    ):
        e1 = client.tag("This is a test", plugin_instance=instance.handle)
        e1.wait()
        assert e1.error is None
        assert count_embeddings(e1.data.file) == 1
        assert len(e1.data.file.blocks[0].tags[0].value["embedding"]) > 1

        e2 = client.tag("This is a test", plugin_instance=instance.handle)
        e2.wait()
        assert e2.error is None
        assert count_embeddings(e2.data.file) == 1
        assert len(e2.data.file.blocks[0].tags[0].value["embedding"]) == len(
            e1.data.file.blocks[0].tags[0].value["embedding"]
        )

        e4 = client.tag("This is a test", plugin_instance=instance.handle)
        e4.wait()
        assert e4.error is None
        assert count_embeddings(e4.data.file) == 1

        # Now lets run all the other embedding tests
        basic_embeddings(client, plugin_instance=instance.handle)
        basic_embedding_search(client, plugin_instance=instance.handle)
        create_index(client, plugin_instance=instance.handle)
