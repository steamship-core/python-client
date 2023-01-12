from steamship_tests import PLUGINS_PATH
from steamship_tests.client.operations.test_embed import (
    basic_embedding_search,
    basic_embeddings,
    count_embeddings,
)
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_name

from steamship.data import TagKind, TagValueKey
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
        assert count_embeddings(e1.output.file) == 1
        assert e1.output.file.blocks[0].tags[0].kind == TagKind.EMBEDDING
        assert len(e1.output.file.blocks[0].tags[0].value[TagValueKey.VECTOR_VALUE]) > 1

        e2 = instance.tag("This is a test")
        e2.wait()
        assert count_embeddings(e2.output.file) == 1
        assert e2.output.file.blocks[0].tags[0].kind == TagKind.EMBEDDING
        assert len(e2.output.file.blocks[0].tags[0].value[TagValueKey.VECTOR_VALUE]) == len(
            e1.output.file.blocks[0].tags[0].value[TagValueKey.VECTOR_VALUE]
        )

        e4 = instance.tag("This is a test")
        e4.wait()
        assert count_embeddings(e4.output.file) == 1

        # Now lets run all the other embedding steamship_tests
        basic_embeddings(instance)
        basic_embedding_search(client, plugin_instance=instance.handle)
        index = client.use_plugin(
            "embedding-index",
            random_name(),
            config={
                "embedder": {
                    "plugin_handle": plugin.handle,
                    "plugin_instance_handle": instance.handle,
                    "fetch_if_exists": True,
                }
            },
            fetch_if_exists=True,
        )
        index.delete()
