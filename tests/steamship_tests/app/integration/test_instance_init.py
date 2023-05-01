from assets.packages.package_verifying_instance_init import PackageWithInstanceInit
from assets.plugins.generators.plugin_with_instance_init import TestGeneratorWithInit
from assets.plugins.taggers.plugin_trainable_tagger import TestTrainableTaggerPlugin
from steamship_tests import PACKAGES_PATH, PLUGINS_PATH
from steamship_tests.utils.client import TESTING_PROFILE
from steamship_tests.utils.deployables import deploy_package, deploy_plugin

from steamship import Steamship
from steamship.data.invocable_init_status import InvocableInitStatus


def test_instance_init_is_called_on_package():
    demo_package_path = PACKAGES_PATH / "package_verifying_instance_init.py"

    with Steamship.temporary_workspace(profile=TESTING_PROFILE) as client:
        with deploy_package(client, demo_package_path, wait_for_init=False) as (_, _, instance):
            assert instance.init_status == InvocableInitStatus.INITIALIZING
            instance.wait_for_init()
            assert instance.init_status == InvocableInitStatus.COMPLETE
            invocation_url = instance.invoke("was_init_called")
            assert invocation_url == instance.invocation_url


def test_plugin_init_dir():
    plugin = TestGeneratorWithInit()
    dir = plugin.__steamship_dir__()
    assert len(dir.get("methods", [])) == 2


def test_package_init_dir():
    package = PackageWithInstanceInit()
    dir = package.__steamship_dir__()
    assert len(dir.get("methods", [])) == 2


def test_instance_init_is_called_on_plugin():
    generator_with_init_path = PLUGINS_PATH / "generators" / "plugin_with_instance_init.py"

    with Steamship.temporary_workspace(profile=TESTING_PROFILE) as client:
        with deploy_plugin(client, generator_with_init_path, "generator", wait_for_init=False) as (
            _,
            _,
            instance,
        ):
            assert instance.init_status == InvocableInitStatus.INITIALIZING
            instance.wait_for_init()
            assert instance.init_status == InvocableInitStatus.COMPLETE

            generate_task = instance.generate(text="Yo! Banana boy!")
            generate_task.wait()
            assert generate_task.output.blocks[0].text == "!yob ananaB !oY"


def test_instance_init_on_trainable_plugin():
    plugin = TestTrainableTaggerPlugin()
    response = plugin.invocable_instance_init()
    assert response.data
