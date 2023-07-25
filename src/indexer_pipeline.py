import json

from steamship import Steamship
from steamship.invocable.mixins import FileType
from steamship.invocable.mixins.blockifier_mixin import BlockifierMixin
from steamship.invocable.mixins.file_importer_mixin import FileImporterMixin
from steamship.invocable.mixins.indexer_mixin import IndexerMixin

with Steamship.temporary_workspace() as client:
    # Init the mixins
    file_importer_mixin = FileImporterMixin(client=client)
    blockifier_mixin = BlockifierMixin(client=client)
    indexer_mixin = IndexerMixin(client=client)

    file_type = FileType.YOUTUBE

    index = client.use_plugin(
        plugin_handle="embedding-index",
        instance_handle="test",
        config={
            "embedder": {
                "plugin_handle": "openai-embedder",
                "plugin_instance_handle": "text-embedding-ada-002",
                "fetch_if_exists": True,
                "config": {"model": "text-embedding-ada-002", "dimensionality": 1536},
            }
        },
        fetch_if_exists=True,
    )

    print(index.index.list_items())

    f, task = file_importer_mixin.import_content(
        content_or_url="https://www.youtube.com/watch?v=LXDZ6aBjv_I",
        file_type=file_type,
    )
    task.wait()

    task = blockifier_mixin.blockify(file_id=f.id, file_type=file_type)

    task.wait()

    index_task = indexer_mixin.index_file(file_id=f.id, index_handle="test")

    print(
        "\n".join([json.loads(item.metadata)["chunk"] for item in index.index.list_items().items])
    )
