import pytest

from steamship import File, Steamship
from steamship.invocable import PackageService
from steamship.invocable.mixins.indexer_pipeline_mixin import IndexerPipelineMixin


@pytest.mark.usefixtures("client")
def test_set_file_status(client: Steamship):
    """Tests that we can inspect the package and mixin routes"""
    file = File.create(client, content="hi")
    invocable = PackageService()
    pipeline = IndexerPipelineMixin(client, invocable)
    pipeline.set_file_status(file_id=file.id, status="FOO")
    file = file.refresh()

    assert len(file.tags) == 1
    tag = file.tags[0]
    assert tag.kind == "status"
    assert tag.name == "FOO"
