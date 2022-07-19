from steamship_tests import PLUGINS_PATH
from steamship_tests.client.operations.test_embed import (
    basic_embedding_search,
    basic_embeddings,
    count_embeddings,
)
from steamship_tests.client.operations.test_embedding_index import create_index
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship.data.plugin import PluginType


def test_e2e_embedder():
    client = get_steamship_client()
    embedder_path = PLUGINS_PATH / "taggers" / "plugin_embedder.py"

    with deploy_plugin(client, embedder_path, PluginType.tagger) as (
        plugin,
        version,
        instance,
    ):
        e1 = instance.tag("This is a test")
        e1.wait()
        assert e1.error is None
        assert count_embeddings(e1.data.file) == 1
        assert len(e1.data.file.blocks[0].tags[0].value["embedding"]) > 1

        e2 = instance.tag("This is a test")
        e2.wait()
        assert e2.error is None
        assert count_embeddings(e2.data.file) == 1
        assert len(e2.data.file.blocks[0].tags[0].value["embedding"]) == len(
            e1.data.file.blocks[0].tags[0].value["embedding"]
        )

        e4 = instance.tag("This is a test")
        e4.wait()
        assert e4.error is None
        assert count_embeddings(e4.data.file) == 1

        # Now lets run all the other embedding steamship_tests
        basic_embeddings(instance)
        basic_embedding_search(client, plugin_instance=instance.handle)
        create_index(client, plugin_instance=instance.handle)
