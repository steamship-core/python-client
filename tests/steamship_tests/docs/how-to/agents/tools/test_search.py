from steamship_tests import DOCS_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Steamship


def test_search_tool():
    with Steamship.temporary_workspace() as client:
        search_agent_path = DOCS_PATH / "how-to/agents-and-tools/agent_with_search_tool.py"
        with deploy_package(client, search_agent_path) as (_, _, instance):
            response = instance.invoke(
                "prompt", prompt="what is the weather in San Fransico today?"
            )
            assert response is not None
