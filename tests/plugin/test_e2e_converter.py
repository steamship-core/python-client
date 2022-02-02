from steamship import App, AppVersion, AppInstance

from ..client.helpers import deploy_app, _steamship, create_app_zip
from steamship import BlockTypes

__copyright__ = "Steamship"
__license__ = "MIT"



def test_instance_invoke():
    steamship = _steamship()
    file = steamship.upload(content="This is a test.").data

    headers = file.query(blockType=BlockTypes.H1).data
    assert(len(headers.blocks) == 0)

    with deploy_app("plugin_converter.py") as (app, version, instance):
        file.convert(model="").wait()

        headers = file.query(blockType=BlockTypes.H1).data
        assert (len(headers.blocks) == 1)
