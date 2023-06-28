import pytest
from steamship_tests import SRC_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Steamship


@pytest.mark.usefixtures("client")
def test_indexer_pipeline_mixin(client: Steamship):
    demo_package_path = SRC_PATH / "steamship" / "agents" / "examples" / "document_qa_agent.py"

    with deploy_package(client, demo_package_path) as (_, version, instance):
        assert version is not None
