from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Block, File


def test_e2e_generator():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "generators" / "test_generator.py"

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
        assert res.output.blocks[0].text == "!yob ananaB !oY"


def test_e2e_generator_with_existing_file():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "generators" / "test_generator.py"

    with deploy_plugin(client, parser_path, "generator") as (
        plugin,
        version,
        instance,
    ):

        # do an all-blocks test
        test_file = File.create(client, blocks=[Block(text="Yo! Banana boy!")])
        res = instance.generate(
            input_file_id=test_file.id, append_output_to_file=True, output_file_id=test_file.id
        )
        res.wait()
        assert res.output is not None
        assert len(res.output.blocks) == 1
        assert res.output.blocks[0].text == "!yob ananaB !oY"

        test_file.refresh()
        assert len(test_file.blocks) == 2
        assert test_file.blocks[1].text == "!yob ananaB !oY"

        # do a some-blocks test
        res = instance.generate(
            input_file_id=test_file.id,
            input_file_start_block_index=1,
            input_file_end_block_index=2,
            append_output_to_file=True,
            output_file_id=test_file.id,
        )
        res.wait()
        assert res.output is not None
        assert len(res.output.blocks) == 1
        assert res.output.blocks[0].text == "Yo! Banana boy!"

        test_file.refresh()
        assert len(test_file.blocks) == 3
        assert test_file.blocks[2].text == "Yo! Banana boy!"


def test_e2e_generator_runtime_options():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "generators" / "test_generator.py"

    with deploy_plugin(client, parser_path, "generator") as (
        plugin,
        version,
        instance,
    ):
        # do an all-blocks test
        test_file = File.create(client, blocks=[Block(text="Yo! Banana boy!")])
        res = instance.generate(
            input_file_id=test_file.id,
            append_output_to_file=True,
            output_file_id=test_file.id,
            options={"test": "yes"},
        )
        res.wait()
        assert res.output is not None
        assert len(res.output.blocks) == 2
        assert res.output.blocks[0].text == "!yob ananaB !oY"
        assert res.output.blocks[1].text == '{"test": "yes"}'
