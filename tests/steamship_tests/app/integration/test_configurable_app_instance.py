from steamship_tests import APPS_PATH
from steamship_tests.utils.deployables import deploy_app
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import PackageInstance


def test_configurable_instance_invoke():
    greeting1 = "Hola"
    config_template = {
        "greeting": {"type": "string"},
        "snake_case_config": {"type": "string"},
        "camelCaseConfig": {"type": "string"},
    }
    instance_config = {
        "greeting": greeting1,
        "snake_case_config": "hisss",
        "camelCaseConfig": "spit!",
    }
    client = get_steamship_client()
    hello_world_path = APPS_PATH / "configurable_hello_world.py"

    with deploy_app(
        client,
        hello_world_path,
        version_config_template=config_template,
        instance_config=instance_config,
    ) as (app, version, instance):
        # Now let's invoke it!
        # Note: we're invoking the data at configurable_hello_world.py in the steamship_tests/demo_apps folder
        res = instance.invoke("greet")
        assert res == f"{greeting1}, Person"

        res = instance.invoke("snake")
        assert res == instance_config.get("snake_case_config")

        res = instance.invoke("camel")
        assert res == instance_config.get("camelCaseConfig")

        greeting2 = "Hallo"
        instance_config2 = {
            "greeting": greeting2,
            "snake_case_config": "hisss",
            "camelCaseConfig": "spit!",
        }
        instance2 = PackageInstance.create(
            client, app_id=app.id, app_version_id=version.id, config=instance_config2
        )

        res2 = instance2.invoke("greet")
        assert res2 == f"{greeting2}, Person"

        # Test with quick-create
        greeting3 = "Howdy"
        instance_config3 = {
            "greeting": greeting3,
            "snake_case_config": "hisss",
            "camelCaseConfig": "spit!",
        }
        instance3 = client.use(app.handle, f"{instance2.handle}-2", config=instance_config3)
        assert instance3.invoke("greet") == f"{greeting3}, Person"
        assert instance3.id != instance2.id

        # Test that quick-create reuses an instance
        instance3a = client.use(app.handle, f"{instance2.handle}-2", config=instance_config3)
        assert instance3a.id == instance3.id

        # Test instance with quick create and no handle
        greeting4 = "How Do Dee"
        instance_config4 = {
            "greeting": greeting4,
            "snake_case_config": "hisss",
            "camelCaseConfig": "spit!",
        }
        instance4 = client.use(app.handle, config=instance_config4)
        assert instance4.invoke("greet") == f"{greeting4}, Person"
        assert instance4.id != instance3.id
