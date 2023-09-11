import pytest
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin

from steamship import Block, Steamship


@pytest.mark.usefixtures("client")
def test_e2e_generator(client: Steamship):
    parser_path = PLUGINS_PATH / "generators" / "test_streaming_generator.py"

    with deploy_plugin(client, parser_path, "generator", streaming=True) as (
        plugin,
        version,
        instance,
    ):
        test_doc = "Yo! Banana boy!"

        # Test unstreamed request
        res = instance.generate(text=test_doc, append_output_to_file=True)
        res.wait()
        assert res.output is not None
        assert len(res.output.blocks) == 1
        assert res.output.blocks[0].text == "!yob ananaB !oY"

        # Test streamed request
        res = instance.generate(text=test_doc, append_output_to_file=True, streaming=True)
        res.wait()
        assert res.output is not None
        assert len(res.output.blocks) == 1
        assert res.output.blocks[0].text == ""  # no text yet!

        streamed_result = str(res.output.blocks[0].raw(), encoding="utf-8")
        assert streamed_result == "!yob ananaB !oY"

        refreshed_block = Block.get(client, _id=res.output.blocks[0].id)
        assert refreshed_block.text == "!yob ananaB !oY"
