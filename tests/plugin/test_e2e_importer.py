from steamship import File
from ..client.helpers import deploy_app, register_app_as_plugin, _steamship
from ..demo_apps.plugin_importer import TEST_DOC

__copyright__ = "Steamship"
__license__ = "MIT"


def test_e2e_importer():
    client = _steamship()
    with deploy_app("plugin_importer.py") as (app, version, instance):
        with register_app_as_plugin(client, "importer", "do_import", app, instance) as plugin:
            file = File.create(
                client=client,
                name="Test.txt",
                content="This is a test.",
                model=plugin.handle
            ).data

            data = file.raw().data

            assert (data.decode('utf-8') == TEST_DOC)

            file.delete()
