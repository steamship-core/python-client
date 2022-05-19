from steamship import AppInstance
from tests import APPS_PATH
from tests.utils.client import get_steamship_client
from tests.utils.deployables import deploy_app


def test_configurable_instance_invoke():
    greeting1 = "Hola"
    config_template = {"greeting": {"type": "string"}}
    instance_config = {"greeting": greeting1}
    client = get_steamship_client()
    hello_world_path = APPS_PATH / "configurable_hello_world.py"

    with deploy_app(
        client,
        hello_world_path,
        version_config_template=config_template,
        instance_config=instance_config,
    ) as (app, version, instance):
        # Now let's invoke it!
        # Note: we're invoking the data at configurable_hello_world.py in the tests/demo_apps folder
        res = instance.post("greet").data
        assert res == f"{greeting1}, Person"

        greeting2 = "Hallo"
        instance_config2 = {"greeting": greeting2}
        instance2 = AppInstance.create(
            client, app_id=app.id, app_version_id=version.id, config=instance_config2
        )
        instance2.wait()
        assert instance2.error is None
        assert instance2.data is not None
        instance2 = instance2.data

        res2 = instance2.post("greet").data
        assert res2 == f"{greeting2}, Person"
