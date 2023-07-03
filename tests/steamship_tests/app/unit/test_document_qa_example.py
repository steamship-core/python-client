import pytest

from steamship import Steamship
from steamship.agents.examples.document_qa_agent import ExampleDocumentQAService
from steamship.utils.url import Verb


@pytest.mark.usefixtures("client")
def test_indexer_pipeline_mixin(client: Steamship):
    package_class = ExampleDocumentQAService

    post_routes = package_class._package_spec.method_mappings[Verb.POST]
    assert "/index_text" in post_routes  # from indexer mixin
    assert "/index_url" in post_routes  # From indexer pipeline mixin
    assert "/blockify_file" in post_routes  # From blockifier mixin
    assert "/import_url" in post_routes  # from file importer mixin
