import json

import pytest
import requests
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Steamship


@pytest.mark.usefixtures("client")
def test_instance_init_is_called_on_package(client: Steamship):
    demo_package_path = PACKAGES_PATH / "echo_test_header.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        url = instance.invocation_url + "/echo_test_header"
        response = requests.get(
            url,
            headers={
                "authorization": f"bearer {client.config.api_key.get_secret_value()}",
                "test1": "testValue1",
                "test2": "testValue2",
            },
        )
        result = json.loads(response.text)
        assert result is not None
        assert result["test1"] == "testValue1"
        assert result["test2"] == "testValue2"
