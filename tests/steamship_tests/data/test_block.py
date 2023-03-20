import pytest
from steamship_tests import TEST_ASSETS_PATH

from steamship import MimeTypes
from steamship.client import Steamship
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags.tag import Tag


@pytest.mark.usefixtures("client")
def test_query(client: Steamship):
    a = File.create(
        client=client,
        blocks=[
            Block(text="A", tags=[Tag(kind="BlockTag")]),
            Block(text="B"),
        ],
    )
    assert a.id is not None
    a = a.refresh()
    b = File.create(
        client=client,
        blocks=[
            Block(text="A"),
            Block(text="B", tags=[Tag(kind="Test")]),
        ],
        tags=[Tag(kind="FileTag")],
    )
    assert b.id is not None
    b = b.refresh()

    blocks = Block.query(client=client, tag_filter_query='blocktag and kind "BlockTag"').blocks
    assert len(blocks) == 1
    assert blocks[0].id == a.blocks[0].id

    blocks = Block.query(client=client, tag_filter_query='blocktag and kind "Test"').blocks
    assert len(blocks) == 1
    assert blocks[0].id == b.blocks[1].id

    a.delete()
    b.delete()


@pytest.mark.usefixtures("client")
def test_append_indices(client: Steamship):
    file = File.create(client, blocks=[Block(text="first")])
    assert len(file.blocks) == 1
    assert file.blocks[0].index_in_file == 0

    appended_block = Block.create(client, file_id=file.id, text="second")
    assert appended_block.index_in_file == 1

    file.refresh()
    assert len(file.blocks) == 2
    assert file.blocks[0].index_in_file == 0
    assert file.blocks[0].text == "first"
    assert file.blocks[1].index_in_file == 1
    assert file.blocks[1].text == "second"


@pytest.mark.usefixtures("client")
def test_append_block_url(client: Steamship):
    file = File.create(client, blocks=[])

    appended_block = Block.create(
        client, file_id=file.id, url="https://docs.steamship.com/_static/Steamship-symbol-dark.png"
    )

    assert appended_block.text == ""
    file.refresh()
    assert len(file.blocks) == 1
    assert file.blocks[0].mime_type == MimeTypes.PNG

    block_content = file.blocks[0].raw()
    assert len(block_content) == 20693
    assert not file.blocks[0].is_text()


@pytest.mark.usefixtures("client")
def test_text_mime_type(client: Steamship):
    file = File.create(client, blocks=[Block(text="first")])
    _ = Block.create(client, file_id=file.id, text="second")
    file.refresh()
    assert len(file.blocks) == 2
    for block in file.blocks:
        assert block.mime_type == MimeTypes.TXT
        assert block.is_text()


@pytest.mark.usefixtures("client")
def test_append_block_content_text(client: Steamship):
    file = File.create(client, blocks=[])

    appended_block = Block.create(client, file_id=file.id, content=bytes("This is a test", "utf-8"))

    assert appended_block.text == "This is a test"
    file.refresh()
    assert len(file.blocks) == 1
    assert file.blocks[0].mime_type == MimeTypes.TXT

    assert file.blocks[0].is_text()


@pytest.mark.usefixtures("client")
def test_append_block_content_image(client: Steamship):
    file = File.create(client, blocks=[])

    palm_tree_path = TEST_ASSETS_PATH / "palm_tree.png"
    with palm_tree_path.open("rb") as f:
        palm_bytes = f.read()

    appended_block = Block.create(
        client, file_id=file.id, content=palm_bytes, mime_type=MimeTypes.PNG
    )

    assert appended_block.text == ""
    file.refresh()
    assert len(file.blocks) == 1
    assert file.blocks[0].mime_type == MimeTypes.PNG

    assert not file.blocks[0].is_text()

    raw_content = file.blocks[0].raw()
    assert raw_content == palm_bytes


@pytest.mark.usefixtures("client")
def test_create_with_tags(client: Steamship):
    file = File.create(client, content="empty")
    new_block = Block.create(
        client,
        file_id=file.id,
        text="foo",
        tags=[Tag(kind="bar", name="foo"), Tag(kind="baz", name="foo")],
    )
    assert len(new_block.tags) == 2


@pytest.mark.usefixtures("client")
def test_append_is_present(client: Steamship):
    file = File.create(client, blocks=[Block(text="first")])
    assert len(file.blocks) == 1

    file.append_block(text="second")
    assert len(file.blocks) == 2

    file.refresh()
    assert len(file.blocks) == 2

    my_file = File.create(client, handle="my_file", content="")
    assert len(my_file.blocks) == 0
    my_file.append_block(text="first")
    assert len(my_file.blocks) == 1
