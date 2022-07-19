import base64

import requests
from steamship_tests import APPS_PATH, TEST_ASSETS_PATH
from steamship_tests.utils.deployables import deploy_app
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Space
from steamship.base import TaskState
from steamship.base.mime_types import MimeTypes
from steamship.data.user import User


def _fix_url(s: str) -> str:
    """Homogenize references to `this machine` for the purpose of comparing remote configuration and local
    configuration. The goal of the below steamship_tests isn't to check that your machine has been configured in the
    "approved way" (which is to use host.docker.internal). It is merely to make sure that the environment
    has been passed to the app instance correctly."""
    s = s.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
    if s.endswith("/"):
        s = s[:-1]  # s.removesuffix is only available in Python 3.9; we use Python 3.8
    return s


def test_instance_invoke():
    palm_tree_path = TEST_ASSETS_PATH / "palm_tree.png"

    with palm_tree_path.open("rb") as f:
        palm_bytes = f.read()
    base64_palm = base64.b64encode(palm_bytes).decode("utf-8")

    client = get_steamship_client()
    demo_app_path = APPS_PATH / "demo_app.py"

    with deploy_app(client, demo_app_path) as (app, version, instance):
        # Now let's invoke it!
        # Note: we're invoking the data at demo_app.py in the steamship_tests/demo_apps folder

        def get_raw(path: str):
            return requests.get(
                instance.full_url_for(path),
                headers={"authorization": f"Bearer {client.config.api_key}"},
            )

        res = instance.get("greet").data
        assert res == "Hello, Person!"

        resp = get_raw("greet")
        assert resp.text == "Hello, Person!"

        res = instance.get("greet", name="Ted").data
        assert res == "Hello, Ted!"
        url = instance.full_url_for("greet?name=Ted")
        resp = requests.get(url, headers={"authorization": f"Bearer {client.config.api_key}"})
        assert resp.text == "Hello, Ted!"

        res = instance.post("greet").data
        assert res == "Hello, Person!"
        url = instance.full_url_for("greet")
        resp = requests.post(url, headers={"authorization": f"Bearer {client.config.api_key}"})
        assert resp.text == "Hello, Person!"

        res = instance.post("greet", name="Ted").data
        assert res == "Hello, Ted!"
        url = instance.full_url_for("greet")
        resp = requests.post(
            url,
            json={"name": "Ted"},
            headers={"authorization": f"Bearer {client.config.api_key}"},
        )
        assert resp.text == "Hello, Ted!"

        # Now we test different return types
        resp_string = get_raw("resp_string")
        assert resp_string.text == "A String"

        resp_dict = get_raw("resp_dict")
        assert resp_dict.json() == {"string": "A String", "int": 10}

        resp_404 = get_raw("doesnt_exist")
        json_404 = resp_404.json()
        assert isinstance(json_404, dict)
        assert json_404.get("status") is not None
        assert json_404.get("status") is not None
        assert json_404.get("status", {}).get("state") == TaskState.failed
        # assert "No handler" in json_404.get("status", dict()).get("statusMessage", "")
        assert resp_404.status_code == 404

        resp_obj = get_raw("resp_obj")
        assert resp_obj.json() == {"name": "Foo"}

        resp_binary = get_raw("resp_binary")
        base64_binary = base64.b64encode(resp_binary.content).decode("utf-8")
        assert base64_binary == base64_palm
        assert resp_binary.headers.get("Content-Type") == MimeTypes.BINARY

        resp_bytes_io = get_raw("resp_bytes_io")
        base64_bytes_io = base64.b64encode(resp_bytes_io.content).decode("utf-8")
        assert base64_bytes_io == base64_palm
        assert resp_bytes_io.headers.get("Content-Type") == MimeTypes.BINARY

        resp_image = get_raw("resp_image")
        base64_image = base64.b64encode(resp_image.content).decode("utf-8")
        assert base64_image == base64_palm
        assert resp_image.headers.get("Content-Type") == MimeTypes.PNG

        # The test app, when executing remotely inside Steamship, should have the same
        # set of configuration options that we're running with here within the test
        configuration_within_lambda_resp = instance.get("config")
        configuration_within_lambda = configuration_within_lambda_resp.data

        my_app_base = _fix_url(client.config.app_base)
        remote_app_base = _fix_url(configuration_within_lambda["appBase"])

        my_api_base = _fix_url(client.config.api_base)
        remote_api_base = _fix_url(configuration_within_lambda["apiBase"])

        assert my_app_base == remote_app_base
        assert my_api_base == remote_api_base
        assert configuration_within_lambda["apiKey"] == client.config.api_key

        # SpaceId is an exception. Rather than being the SpaceId of the client, it should be the SpaceId
        # of the App Instance.
        assert configuration_within_lambda["spaceId"] == instance.space_id  # SpaceID

        # The test app, when executing remotely inside Steamship, should have the same
        # user that we're running with here in within the test
        user_info = instance.post("user_info")
        user = User.current(client)
        assert user_info.data["handle"] == user.data.handle


def test_deploy_in_space():
    client = get_steamship_client()
    demo_app_path = APPS_PATH / "demo_app.py"

    space = Space.create(client, handle="test-non-default-space").data
    with deploy_app(client, demo_app_path, space_id=space.id) as (_, _, instance):
        assert instance.space_id == space.id
