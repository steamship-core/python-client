from typing import Dict

import pytest
from assets.packages.transports.mock_telegram_package import MockTelegram
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import File, Steamship

config_template = {
    "bot_token": {"type": "string"},
    "api_base": {"type": "string"},
}


@pytest.mark.usefixtures("client")
def test_telegram(client: Steamship):

    mock_telegram_package_path = PACKAGES_PATH / "transports" / "mock_telegram_package.py"
    telegram_agent_path = PACKAGES_PATH / "transports" / "test_telegram_agent.py"

    with deploy_package(client, mock_telegram_package_path) as (_, _, mock_telegram_instance):

        # Removing the / from the invocation URL and passing it as the bot_token allows
        # the bot token to not be empty and the two appended to each other to just equal the
        # invocation url.
        instance_config = {"bot_token": "/", "api_base": mock_telegram_instance.invocation_url[:-1]}
        with deploy_package(
            client,
            telegram_agent_path,
            version_config_template=config_template,
            instance_config=instance_config,
        ) as (_, _, telegram_instance):

            # Test that agent called instance_init and registered webhook
            files = File.query(client, f'kind "{MockTelegram.WEBHOOK_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].name == telegram_instance.invocation_url + "respond"

            # test sending messages
            telegram_instance.invoke("respond", **generate_telegram_message("a test"))
            files = File.query(client, f'kind "{MockTelegram.TEXT_MESSAGE_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].name == "Response to: a test".replace(
                " ", "+"
            )  # bug somewhere - results being url encoded
            assert files[0].tags[0].value == {MockTelegram.CHAT_ID_KEY: 1}

            # test sending another message; this has been a problem before
            telegram_instance.invoke("respond", **generate_telegram_message("another test"))
            files = File.query(client, f'kind "{MockTelegram.TEXT_MESSAGE_TAG}"').files
            assert len(files) == 2
            for file in files:
                assert file.tags[0].name in [
                    "Response to: a test".replace(" ", "+"),
                    "Response to: another test".replace(" ", "+"),
                ]  # bug somewhere - results being url encoded
                assert file.tags[0].value == {MockTelegram.CHAT_ID_KEY: 1}


def generate_telegram_message(text: str) -> Dict:
    return {
        "update_id": 1,
        "message": {"message_id": 1, "chat": {"id": 1}, "text": text},
    }
