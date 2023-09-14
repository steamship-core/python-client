import pytest
import requests
from assets.packages.transports.mock_slack_api import MockSlackApi
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import File, Steamship

config_template = {
    "telegram_token": {"type": "string"},
    "telegram_api_base": {"type": "string"},
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
            "telegram_token": "",
            "telegram_api_base": "",
        }

        with deploy_package(
            client,
            transport_agent_path,
            version_config_template=config_template,
            instance_config=instance_config,
            wait_for_init=True,
        ) as (_, _, agent_instance):
            # Set the bot token
            is_token_set_no = agent_instance.invoke("is_slack_token_set")
            assert is_token_set_no is False

            agent_instance.invoke("set_slack_access_token", token="")  # noqa: S106
            is_token_set_true = agent_instance.invoke("is_slack_token_set")
            assert is_token_set_true is True

            # Note: this is the synchronous respond method which is easier to test.
            # The actual Slack webhook calls this async in order to respond within Slack's required latency.
            respond_method = "slack_respond_sync"

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
            allowed_responses = ["Response to: a test", "Response to: a test".replace(" ", "+")]
            assert (
                files[0].tags[0].name in allowed_responses
            )  # bug somewhere - results being url encoded in some envs
            assert files[0].tags[0].value == {MockSlackApi.CHAT_ID_KEY: "1"}

            # test sending another message; this has been a problem before
            agent_instance.invoke(
                respond_method, **MockSlackApi.generate_inbound_webhook_body("another test")
            )
            files = File.query(client, f'kind "{MockSlackApi.TEXT_MESSAGE_TAG}"').files
            assert len(files) == 2
            allowed_responses.extend(
                ["Response to: another test", "Response to: another test".replace(" ", "+")]
            )
            for file in files:
                assert (
                    file.tags[0].name in allowed_responses
                )  # bug somewhere - results being url encoded in some envs
                assert file.tags[0].value == {MockSlackApi.CHAT_ID_KEY: "1"}

            # Test the agent sending a "photo"
            agent_instance.invoke(
                respond_method, **MockSlackApi.generate_inbound_webhook_body("image")
            )
            files = File.query(client, f'kind "{MockSlackApi.PHOTO_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].value.get(MockSlackApi.CHAT_ID_KEY) == "1"
            assert client.config.api_base in files[0].tags[0].value.get(MockSlackApi.PHOTO_KEY)

            # Test the agent sending "audio"
            agent_instance.invoke(
                respond_method, **MockSlackApi.generate_inbound_webhook_body("audio")
            )
            files = File.query(client, f'kind "{MockSlackApi.AUDIO_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].value.get(MockSlackApi.CHAT_ID_KEY) == "1"
            assert client.config.api_base in files[0].tags[0].value.get(MockSlackApi.AUDIO_KEY)

            # Test the agent sending a "video"
            agent_instance.invoke(
                respond_method, **MockSlackApi.generate_inbound_webhook_body("video")
            )
            files = File.query(client, f'kind "{MockSlackApi.VIDEO_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].value.get(MockSlackApi.CHAT_ID_KEY) == "1"
            assert client.config.api_base in files[0].tags[0].value.get(MockSlackApi.VIDEO_KEY)
