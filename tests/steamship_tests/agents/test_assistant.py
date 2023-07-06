import json

import pytest
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Steamship, Task, TaskState


@pytest.mark.usefixtures("client")
def test_async_run(client: Steamship):
    demo_package_path = PACKAGES_PATH / "assistant_package.py"

    with deploy_package(client, demo_package_path, wait_for_init=False) as (_, _, instance):
        instance.wait_for_init()

        out_json = instance.invoke(
            "/async_prompt", prompt="draw me a picture of a cat in a silly hat"
        )
        out_dict = json.loads(out_json)

        task = Task.get(client=client, _id=out_dict.get("task_id"))
        while task.state not in [TaskState.succeeded, TaskState.failed]:
            steps = instance.invoke("/completed_steps", file_handle=out_dict.get("file_handle"))
            print("---")
            print(steps)
            try:
                task.wait(max_timeout_s=5)
                task.refresh()
            except:
                print("async waiting continues...")

        print("finished!")
        steps = instance.invoke("/completed_steps", file_handle=out_dict.get("file_handle"))
        print("---")
        print(steps)
