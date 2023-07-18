import pytest
import requests
from assets.packages.transports.mock_slack_api import MockSlackApi
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import File, Steamship

config_template = {
    "bot_token": {"type": "string"},
    "api_base": {"type": "string"},
    "slack_api_base": {"type": "string"},
}


@pytest.mark.usefixtures("client")
def test_slack(client: Steamship):

    mock_slack_api_path = PACKAGES_PATH / "transports" / "mock_slack_api.py"
    transport_agent_path = PACKAGES_PATH / "transports" / "test_transports_agent.py"

    with deploy_package(client, mock_slack_api_path) as (_, _, mock_chat_api):

        # Set the slack_api_base to the mock Slack API we just deployed.
        # This will allow us to test for the proper receipt of messages.
        instance_config = {
            "slack_api_base": mock_chat_api.invocation_url,
            "bot_token": "",
            "api_base": "",
        }

        with deploy_package(
            client,
            transport_agent_path,
            version_config_template=config_template,
            instance_config=instance_config,
        ) as (_, _, agent_instance):

            respond_method = "slack_respond"

            # Set the response URL
            response_url = agent_instance.invocation_url
            if not response_url.endswith("/"):
                response_url = response_url + "/"
            response_url = response_url + respond_method

            # Test sending messages (without auth)
            response = requests.post(
                url=response_url,
                json=MockSlackApi.generate_inbound_webhook_body("a test"),
            )
            assert response.ok
            files = File.query(client, f'kind "{MockSlackApi.TEXT_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].name == "Response to: a test".replace(
                " ", "+"
            )  # bug somewhere - results being url encoded
            assert files[0].tags[0].value == {MockSlackApi.CHAT_ID_KEY: 1}

            # test sending another message; this has been a problem before
            agent_instance.invoke(
                respond_method, **MockSlackApi.generate_inbound_webhook_body("another test")
            )
            files = File.query(client, f'kind "{MockSlackApi.TEXT_MESSAGE_TAG}"').files
            assert len(files) == 2
            for file in files:
                assert file.tags[0].name in [
                    "Response to: a test".replace(" ", "+"),
                    "Response to: another test".replace(" ", "+"),
                ]  # bug somewhere - results being url encoded
                assert file.tags[0].value == {MockSlackApi.CHAT_ID_KEY: 1}

            # Test the agent sending a "photo"
            agent_instance.invoke(
                respond_method, **MockSlackApi.generate_inbound_webhook_body("image")
            )
            files = File.query(client, f'kind "{MockSlackApi.PHOTO_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].value == {
                MockSlackApi.CHAT_ID_KEY: 1,
                MockSlackApi.PHOTO_KEY: "some image bytes",
            }

            # Test the agent sending "audio"
            agent_instance.invoke(
                respond_method, **MockSlackApi.generate_inbound_webhook_body("audio")
            )
            files = File.query(client, f'kind "{MockSlackApi.AUDIO_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].value == {
                MockSlackApi.CHAT_ID_KEY: 1,
                MockSlackApi.AUDIO_KEY: "some audio bytes",
            }

            # Test the agent sending a "video"
            agent_instance.invoke(
                respond_method, **MockSlackApi.generate_inbound_webhook_body("video")
            )
            files = File.query(client, f'kind "{MockSlackApi.VIDEO_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].value == {
                MockSlackApi.CHAT_ID_KEY: 1,
                MockSlackApi.VIDEO_KEY: "some video bytes",
            }
