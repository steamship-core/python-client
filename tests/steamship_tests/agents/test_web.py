import pytest
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Steamship


@pytest.mark.usefixtures("client")
def test_web(client: Steamship):

    web_agent_path = PACKAGES_PATH / "transports" / "test_web_agent.py"

    with deploy_package(
        client,
        web_agent_path,
    ) as (_, _, web_instance):

        response = web_instance.invoke("answer", question="test")
        assert response[0].get("text") == "Response to: test"

        # Test multiple times since we previously had issues on subsequent calls
        response = web_instance.invoke("answer", question="test2")
        assert response[0].get("text") == "Response to: test2"

        response = web_instance.invoke("answer", question="test3")
        assert response[0].get("text") == "Response to: test3"
