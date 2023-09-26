import pytest
import requests
from assets.packages.transports.mock_telegram_api import MockTelegramApi
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import File, PackageInstance, Steamship
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.agents.service.agent_service import AgentService

config_template = {
    "telegram_token": {"type": "string", "default": ""},
    "telegram_api_base": {"type": "string", "default": ""},
    "slack_api_base": {"type": "string", "default": ""},
}


def test_telegram_api_base():
    with Steamship.temporary_workspace() as client:
        transport = TelegramTransport(
            client=client,
            agent_service=AgentService(client=client),
            config=TelegramTransportConfig(),
        )
        transport.bot_token = "TOKEN"  # noqa: S105
        assert transport.get_api_root() == "https://api.telegram.org/botTOKEN"


@pytest.mark.usefixtures("client")
def test_telegram(client: Steamship):

    mock_telegram_api_path = PACKAGES_PATH / "transports" / "mock_telegram_api.py"
    telegram_agent_path = PACKAGES_PATH / "transports" / "test_transports_agent.py"

    with deploy_package(client, mock_telegram_api_path, wait_for_init=True) as (
        _,
        _,
        mock_chat_api,
    ):
        # Test that the default instance doesn't have an API set.

        # Removing the / from the invocation URL and passing it as the telegram_token allows
        # the bot token to not be empty and the two appended to each other to just equal the
        # invocation url.
        instance_config = {
            "telegram_token": "abcdefg",
            "telegram_api_base": mock_chat_api.invocation_url[:-1],
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

        files = File.query(client, f'kind "{MockTelegramApi.WEBHOOK_TAG}"').files
        assert len(files) == 0

        with deploy_package(
            client,
            telegram_agent_path,
            version_config_template=config_template,
            instance_config=instance_config,
            wait_for_init=True,
        ) as (agent_package, agent_version, agent_instance):
            respond_method = "telegram_respond"

            # The configuration provided a token, so the token should be reported as having been set.
            assert agent_instance.invoke("is_telegram_token_set") is True

            # The telegram_bot_info should return {"username": "TestBot"}
            assert agent_instance.invoke("telegram_bot_info") == {"username": "TestBot"}

            # Test that agent called instance_init and registered webhook
            files = File.query(client, f'kind "{MockTelegramApi.WEBHOOK_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].name == agent_instance.invocation_url + respond_method

            files[0].delete()

            files = File.query(client, f'kind "{MockTelegramApi.WEBHOOK_TAG}"').files
            assert len(files) == 0

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

            # Verify that we don't have any webhook set files
            files = File.query(client, f'kind "{MockTelegramApi.WEBHOOK_TAG}"').files
            assert len(files) == 0

            agent_instance.invoke("set_telegram_access_token", token="foo-bar")  # noqa: S106

            # Test that this triggered a web hook reset
            files = File.query(client, f'kind "{MockTelegramApi.WEBHOOK_TAG}"').files
            assert len(files) == 1

            files[0].delete()

            # Create another instance to test LATE BOUND Telegram connections.

            instance_config_without_token = {
                "telegram_api_base": mock_chat_api.invocation_url[:-1],
                "slack_api_base": mock_chat_api.invocation_url,
            }

            package_instance_2 = PackageInstance.create(
                client,
                package_id=agent_package.id,
                package_version_id=agent_version.id,
                config=instance_config_without_token,
            )

            package_instance_2.wait_for_init()

            # The configuration provided a token, so the token should be reported as having been set.
            assert package_instance_2.invoke("is_telegram_token_set") is False

            package_instance_2.invoke(
                "set_telegram_access_token", token=instance_config.get("telegram_token")
            )

            assert package_instance_2.invoke("is_telegram_token_set") is True

            # See that the webhook was registered
            files = File.query(client, f'kind "{MockTelegramApi.WEBHOOK_TAG}"').files
            assert len(files) == 1
