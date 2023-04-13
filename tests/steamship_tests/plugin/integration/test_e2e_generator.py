from assets.plugins.generators.test_generator_returns_bytes import TEST_BYTES_STRING
from steamship_tests import PLUGINS_PATH, TEST_ASSETS_PATH
from steamship_tests.utils.deployables import deploy_plugin
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Block, File, MimeTypes, PluginInstance


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

        # do an index-list test
        test_file = File.create(
            client,
            blocks=[
                Block(text="Yo! Banana boy!"),
                Block(text="A man, a plan, a canal, Panama!"),
                Block(text="Tacocat!"),
            ],
        )
        res = instance.generate(input_file_id=test_file.id, input_file_block_index_list=[0, 2])
        res.wait()
        assert res.output is not None
        assert len(res.output.blocks) == 2
        assert res.output.blocks[0].text == "!yob ananaB !oY"
        assert res.output.blocks[1].text == "!tacocaT"


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


def test_generator_ephemeral_image_output():
    client = get_steamship_client()
    plugin_instance = PluginInstance.create(client, plugin_handle="test-image-generator")
    generate_task = plugin_instance.generate(text="This won't be used")

    generate_task.wait()
    assert generate_task.output is not None
    assert len(generate_task.output.blocks) == 1
    assert generate_task.output.blocks[0].content_url is not None
    data = generate_task.output.blocks[0].raw()
    assert data.decode("UTF-8") == "PRETEND THIS IS THE DATA OF AN IMAGE"


def test_e2e_generate_from_image():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "generators" / "test_image_to_text_generator.py"

    with deploy_plugin(client, parser_path, "generator") as (
        _,
        _,
        generator,
    ):
        test_file = File.create(client, content="")
        palm_tree_path = TEST_ASSETS_PATH / "palm_tree.png"

        with palm_tree_path.open("rb") as f:
            palm_bytes = f.read()
        block = Block.create(
            client, file_id=test_file.id, content=palm_bytes, mime_type=MimeTypes.PNG
        )

        fetched_bytes = block.raw()

        assert palm_bytes == fetched_bytes

        generate_task = generator.generate(input_file_id=test_file.id)
        generate_task.wait()
        result = generate_task.output.blocks[0].text
        assert result == "Found 1 image blocks and fetched data from 1"


def test_e2e_generate_returning_bytes():
    client = get_steamship_client()
    parser_path = PLUGINS_PATH / "generators" / "test_generator_returns_bytes.py"

    with deploy_plugin(client, parser_path, "generator") as (
        _,
        _,
        generator,
    ):

        # Test ephemerally
        generate_task = generator.generate(text="")
        generate_task.wait()

        ephemeral_block = generate_task.output.blocks[0]
        assert ephemeral_block.content_url is not None
        ephemeral_block_content = ephemeral_block.raw()
        assert ephemeral_block_content == TEST_BYTES_STRING.encode("utf-8")

        # test persisted
        generate_task_persist = generator.generate(text="", append_output_to_file=True)
        generate_task_persist.wait()
        persisted_block = generate_task_persist.output.blocks[0]
        assert persisted_block.content_url is None
        assert persisted_block.file_id is not None
        persisted_block_content = persisted_block.raw()
        assert persisted_block_content == TEST_BYTES_STRING.encode("utf-8")
