import pytest
import requests
from assets.packages.transports.mock_telegram_api import MockTelegramApi
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import File, Steamship

config_template = {
    "bot_token": {"type": "string"},
    "api_base": {"type": "string"},
    "slack_api_base": {"type": "string"},
}


@pytest.mark.usefixtures("client")
def test_telegram(client: Steamship):

    mock_telegram_api_path = PACKAGES_PATH / "transports" / "mock_telegram_api.py"
    telegram_agent_path = PACKAGES_PATH / "transports" / "test_transports_agent.py"

    with deploy_package(client, mock_telegram_api_path) as (_, _, mock_chat_api):

        # Removing the / from the invocation URL and passing it as the bot_token allows
        # the bot token to not be empty and the two appended to each other to just equal the
        # invocation url.
        instance_config = {
            "bot_token": "/",
            "api_base": mock_chat_api.invocation_url[:-1],
            "slack_api_base": mock_chat_api.invocation_url,
        }

        # Should be able to invoke setWebhook publicly
        response = requests.get(
            url=mock_chat_api.invocation_url + "/setWebhook",
            params={"url": "test", "allowed_updates": "", "drop_pending_updates": True},
        )
        assert response.ok
        # Test that the call to setWebhook wrote a file
        files = File.query(client, f'kind "{MockTelegramApi.WEBHOOK_TAG}"').files
        assert len(files) == 1
        assert files[0].tags[0].name == "test"

        files[0].delete()

        with deploy_package(
            client,
            telegram_agent_path,
            version_config_template=config_template,
            instance_config=instance_config,
        ) as (_, _, agent_instance):
            respond_method = "telegram_respond"

            # Test that agent called instance_init and registered webhook
            files = File.query(client, f'kind "{MockTelegramApi.WEBHOOK_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].name == agent_instance.invocation_url + respond_method

            # test sending messages (without auth)
            response = requests.post(
                url=agent_instance.invocation_url + f"/{respond_method}",
                json=MockTelegramApi.generate_inbound_webhook_body("a test"),
            )
            assert response.ok
            files = File.query(client, f'kind "{MockTelegramApi.TEXT_MESSAGE_TAG}"').files
            assert len(files) == 1

            assert (
                files[0].tags[0].name == "Response to: a test"
            )  # bug somewhere - results being url encoded in some envs

            assert files[0].tags[0].value == {MockTelegramApi.CHAT_ID_KEY: 1}

            # test sending another message; this has been a problem before
            agent_instance.invoke(
                respond_method, **MockTelegramApi.generate_inbound_webhook_body("another test")
            )
            files = File.query(client, f'kind "{MockTelegramApi.TEXT_MESSAGE_TAG}"').files
            assert len(files) == 2
            allowed_responses = ["Response to: a test", "Response to: another test"]
            for file in files:
                assert file.tags[0].name in allowed_responses
                assert file.tags[0].value == {MockTelegramApi.CHAT_ID_KEY: 1}

            # Test the agent sending a "photo"
            agent_instance.invoke(
                respond_method, **MockTelegramApi.generate_inbound_webhook_body("image")
            )
            files = File.query(client, f'kind "{MockTelegramApi.PHOTO_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].value == {
                MockTelegramApi.CHAT_ID_KEY: 1,
                MockTelegramApi.PHOTO_KEY: "some image bytes",
            }

            # Test the agent sending "audio"
            agent_instance.invoke(
                respond_method, **MockTelegramApi.generate_inbound_webhook_body("audio")
            )
            files = File.query(client, f'kind "{MockTelegramApi.AUDIO_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].value == {
                MockTelegramApi.CHAT_ID_KEY: 1,
                MockTelegramApi.AUDIO_KEY: "some audio bytes",
            }

            # Test the agent sending a "video"
            agent_instance.invoke(
                respond_method, **MockTelegramApi.generate_inbound_webhook_body("video")
            )
            files = File.query(client, f'kind "{MockTelegramApi.VIDEO_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].value == {
                MockTelegramApi.CHAT_ID_KEY: 1,
                MockTelegramApi.VIDEO_KEY: "some video bytes",
            }
