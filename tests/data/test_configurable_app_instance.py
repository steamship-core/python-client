import requests

from steamship import AppInstance
from steamship.data.user import User
from tests.client.helpers import _steamship, deploy_app, shouldUseSubdomain

__copyright__ = "Steamship"
__license__ = "MIT"


def test_configurable_instance_invoke():

    greeting1 = "Hola"
    configTemplate = { "greeting" : {"type": "string"}}
    instanceConfig = { "greeting" : greeting1}

    with deploy_app("configurable_hello_world.py", versionConfigTemplate=configTemplate, instanceConfig=instanceConfig) as (app, version, instance):
        # Now let's invoke it!
        # Note: we're invoking the data at configurable_hello_world.py in the tests/demo_apps folder
        client = _steamship()
        res = instance.post('greet').data
        assert (res == "{}, Person".format(greeting1))


        greeting2 = "Hallo"
        instanceConfig2 = { "greeting" : greeting2}
        instance2 = AppInstance.create(
            client,
            appId=app.id,
            appVersionId=version.id,
            config=instanceConfig2
        )
        instance2.wait()
        assert (instance2.error is None)
        assert (instance2.data is not None)
        instance2 = instance2.data

        res2 = instance2.post('greet').data
        assert (res2 == "{}, Person".format(greeting2))

