import base64
import json
import re

import pytest
import requests
from steamship_tests import PACKAGES_PATH, TEST_ASSETS_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import PackageInstance, SteamshipError, Task, Workspace
from steamship.base import TaskState
from steamship.base.mime_types import MimeTypes
from steamship.utils.url import Verb


def _fix_url(s: str) -> str:
    """Homogenize references to `this machine` for the purpose of comparing remote configuration and local
    configuration. The goal of the below steamship_tests isn't to check that your machine has been configured in the
    "approved way" (which is to use host.docker.internal). It is merely to make sure that the environment
    has been passed to the invocable instance correctly."""
    s = s.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
    if s.endswith("/"):
        s = s[:-1]  # s.removesuffix is only available in Python 3.9; we use Python 3.8
    return s


@pytest.mark.xfail()
def test_instance_invoke():
    palm_tree_path = TEST_ASSETS_PATH / "palm_tree.png"

    with palm_tree_path.open("rb") as f:
        palm_bytes = f.read()
    base64_palm = base64.b64encode(palm_bytes).decode("utf-8")

    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "demo_package.py"

    with deploy_package(client, demo_package_path) as (package, version, instance):
        # Now let's invoke it!
        # Note: we're invoking the data at demo_package.py in the tests/assets/packages folder

        def get_raw(path: str):
            return requests.get(
                instance.full_url_for(path),
                headers={"authorization": f"Bearer {client.config.api_key}"},
            )

        res = instance.invoke("greet", verb=Verb.GET)
        assert res == "Hello, Person!"

        resp = get_raw("greet")
        assert resp.text == "Hello, Person!"

        res = instance.invoke("greet", verb=Verb.GET, name="Ted")
        assert res == "Hello, Ted!"
        url = instance.full_url_for("greet?name=Ted")
        resp = requests.get(url, headers={"authorization": f"Bearer {client.config.api_key}"})
        assert resp.text == "Hello, Ted!"

        res = instance.invoke("greet", verb=Verb.POST)
        assert res == "Hello, Person!"
        url = instance.full_url_for("greet")
        resp = requests.post(url, headers={"authorization": f"Bearer {client.config.api_key}"})
        assert resp.text == "Hello, Person!"

        res = instance.invoke("greet", verb=Verb.POST, name="Ted")
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

        # The test invocable, when executing remotely inside Steamship, should have the same
        # set of configuration options that we're running with here within the test
        configuration_within_lambda = instance.invoke("config", verb=Verb.GET)

        my_app_base = _fix_url(client.config.app_base)
        remote_app_base = _fix_url(configuration_within_lambda["appBase"])

        my_api_base = _fix_url(client.config.api_base)
        remote_api_base = _fix_url(configuration_within_lambda["apiBase"])

        assert my_app_base == remote_app_base
        assert my_api_base == remote_api_base

        # API key should NOT be the same as the original, because the invocable should be given a workspace-scoped key
        assert configuration_within_lambda["apiKey"] != client.config.api_key

        # WorkspaceId is an exception. Rather than being the WorkspaceId of the client, it should be the WorkspaceId
        # of the App Instance.
        assert configuration_within_lambda["workspaceId"] == instance.workspace_id  # WorkspaceID

        # The test invocable should NOT be able to fetch the User's account info.
        with pytest.raises(SteamshipError) as excinfo:
            _ = instance.invoke("user_info", verb=Verb.POST)
        assert "Cannot use a workspace-scoped key" in str(excinfo.value)

        # Test a JSON response that contains {"status": "a string"} in it to make sure the client base
        # isn't trying to coerce it to a Task object and throwing.
        resp_obj = instance.invoke("json_with_status", verb=Verb.POST)
        assert resp_obj == {"status": "a string"}

        # Test that the __steamship_dir__ method works
        #
        # Note: The output of the InvocableResponse includes a dynamically generated value:
        #
        #       returns': "<class 'l_dd6730cb.InvocableResponse[bytes]'>"
        #
        # So we've got to do a little regex switcheroo

        search_pattern = r"'[a-zA-Z0-9_]+\.InvocableResponse\["
        replace_pattern = "'foo.InvocableResponse["

        def replace_string(s: str):
            return re.sub(search_pattern, replace_pattern, s)

        steamship_dir = instance.invoke("__dir__")
        with open(TEST_ASSETS_PATH / "demo_package_spec.json", "r") as f:
            steamship_dir_golden = json.loads(replace_string(f.read()))
            steamship_dir_fixed = json.loads(replace_string(json.dumps(steamship_dir)))
            assert steamship_dir_fixed == steamship_dir_golden

        # Test that we can call a task which SCHEDULES another task
        future_greet_resp = instance.invoke("future_greet", name="Unicorn")
        future_task = Task(client=client, **future_greet_resp)
        future_task.wait()
        future_task_bytes = base64.b64decode(future_task.output)
        future_task_string = future_task_bytes.decode("utf-8")
        assert future_task_string == "Hello, Unicorn!"

        # Test that we can call a task which SCHEDULES another task itself dependent on another task
        future_greet_resp2 = instance.invoke("future_greet_then_greet_again", name="Decacorn")
        future_task2 = Task(client=client, **future_greet_resp2)
        future_task2.wait()
        future_task_bytes2 = base64.b64decode(future_task2.output)
        future_task_string2 = future_task_bytes2.decode("utf-8")
        assert future_task_string2 == "Hello, Decacorn 2!"


def test_deploy_in_workspace():
    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "demo_package.py"

    workspace = Workspace.create(client)
    client.switch_workspace(workspace_id=workspace.id)

    assert workspace.handle != "default"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        # The Engine believes the instance to be in the workspace
        assert instance.workspace_id == workspace.id

        # The invocable believes itself to be in the workspace
        configuration_within_lambda = instance.invoke("config", verb=Verb.GET)
        assert configuration_within_lambda["workspaceId"] == workspace.id

    workspace.delete()


def test_package_instance_get():
    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "demo_package.py"

    workspace = Workspace.create(client)
    client.switch_workspace(workspace_id=workspace.id)

    assert workspace.handle != "default"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        instance_handle = instance.handle
        other_instance = PackageInstance.get(client, instance_handle)
        assert other_instance.id == instance.id
        assert other_instance.handle == instance.handle
        assert other_instance.package_id == instance.package_id
        assert other_instance.package_version_id == instance.package_version_id


def test_plugin_instance_handle_refs():
    steamship = get_steamship_client()

    demo_package_path = PACKAGES_PATH / "demo_package.py"

    workspace = Workspace.create(steamship)
    steamship.switch_workspace(workspace_id=workspace.id)

    assert workspace.handle != "default"

    with deploy_package(steamship, demo_package_path) as (package, version, instance):

        assert instance.package_handle == package.handle
        assert instance.package_version_handle == version.handle

        got_instance = PackageInstance.get(steamship, instance.handle)

        assert got_instance.package_handle == package.handle
        assert got_instance.package_version_handle == version.handle

        use_instance = steamship.use(package_handle=package.handle, version=version.handle)
        assert use_instance.package_handle == package.handle
        assert use_instance.package_version_handle == version.handle
