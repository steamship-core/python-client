from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship.base import SteamshipError


def test_task_timeout():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "taggers" / "plugin_parser.py"
    # TODO (enias): Use Enum for plugin type
    with deploy_plugin(client, parser_path, "tagger", safe_load_handler=True) as (
        plugin,
        version,
        instance,
    ):
        test_doc = "Hi there"
        res = instance.tag(doc=test_doc)
        try:
            res.wait(max_timeout_s=0.01, retry_delay_s=0.01)
            raise AssertionError("The call to wait() should throw")
        except SteamshipError:
            pass
