from assets.plugins.generators.async_generator import OUTPUT_BLOCK_TEXT
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client


def test_e2e_generator():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "generators" / "async_generator.py"

    with deploy_plugin(client, parser_path, "generator") as (
        plugin,
        version,
        instance,
    ):
        test_doc = "Yo! Banana boy!"
        res = instance.generate(text=test_doc, append_output_to_file=False)
        res.wait()
        assert res.output is not None
        assert len(res.output.blocks) == 1
        assert res.output.blocks[0].text == OUTPUT_BLOCK_TEXT
