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
        instance_config = {"bot_token": "/", "api_base": mock_telegram_instance.invocation_url}
        with deploy_package(
            client,
            telegram_agent_path,
            version_config_template=config_template,
            instance_config=instance_config,
        ) as (_, _, telegram_instance):
            files = File.query(client, f'kind "{MockTelegram.WEBHOOK_TAG}"').files
            assert len(files) == 1
            assert files[0].tags[0].name == telegram_instance.invocation_url + "respond"
