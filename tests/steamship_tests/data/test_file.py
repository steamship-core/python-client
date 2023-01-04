import json

import pytest
from steamship_tests import PLUGINS_PATH
from steamship_tests.utils.deployables import deploy_plugin

from steamship import MimeTypes, SteamshipError
from steamship.client import Steamship
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags.tag import Tag


@pytest.mark.usefixtures("client")
def test_file_upload(client: Steamship):
    a = File.create(client=client, handle="foo", content="A", mime_type=MimeTypes.MKD)
    assert a.id is not None
    assert a.mime_type == MimeTypes.MKD
    assert a.handle == "foo"

    b = File.create(client=client, content="B", mime_type=MimeTypes.TXT)
    assert b.id is not None
    assert b.mime_type == MimeTypes.TXT
    assert a.id != b.id
    assert a.raw().decode("utf-8") == "A"
    a.delete()
    b.delete()


@pytest.mark.usefixtures("client")
def test_only_blocks_or_content(client: Steamship):
    with pytest.raises(SteamshipError):
        _ = File.create(client=client, content="A", blocks=[], mime_type=MimeTypes.MKD)


@pytest.mark.usefixtures("client")
def test_file_upload_with_content_and_tags(client: Steamship):
    a = File.create(
        client=client,
        content="ABC",
        mime_type=MimeTypes.MKD,
        tags=[Tag(kind="SomeKind")],
    )
    assert a.id is not None
    assert a.mime_type == MimeTypes.MKD
    assert len(a.tags) == 1
    assert a.tags[0].file_id == a.id
    assert a.tags[0].kind == "SomeKind"
    assert a.raw().decode("utf-8") == "ABC"


def test_file_import_response_dict():
    resp = File.CreateResponse(_bytes=b"some bytes", mime_type=MimeTypes.BINARY)
    to_dict = resp.dict(include={"data_", "mime_type"})
    file_create_response = File.CreateResponse.parse_obj(to_dict)
    assert resp.data_ == file_create_response.data_
    assert resp.mime_type == file_create_response.mime_type


def test_file_import_response_bytes_serialization():
    file_resp = File.CreateResponse(_bytes=b"some bytes", mime_type=MimeTypes.BINARY)
    to_dict = file_resp.dict()
    as_json_string = json.dumps(to_dict)
    as_dict_again = json.loads(as_json_string)
    assert as_dict_again == to_dict


def test_file_upload_with_blocks(client: Steamship):
    a = File.create(
        client=client,
        blocks=[
            Block(text="A", tags=[Tag(kind="BlockTag")]),
            Block(text="B", tags=[Tag(kind="BlockTag")]),
        ],
    )
    assert a.id is not None

    query_result = Block.query(client, f'file_id "{a.id}"')

    def check_blocks(block_list):
        assert len(block_list) == 2
        assert block_list[0].tags is not None
        assert len(block_list[0].tags) == 1
        assert block_list[0].tags[0].kind == "BlockTag"
        assert block_list[0].text == "A"

    assert query_result.blocks is not None
    check_blocks(query_result.blocks)

    # Let's get the file fresh
    aa = File.get(client, _id=a.id)
    check_blocks(aa.blocks)
    a.delete()


def test_file_upload_with_blocks_and_tags(client: Steamship):
    a = File.create(
        client=client,
        blocks=[
            Block(text="A", tags=[Tag(kind="BlockTag")]),
            Block(text="B", tags=[Tag(kind="BlockTag")]),
        ],
        tags=[Tag(kind="FileTag")],
    )
    assert a.id is not None

    blocks = Block.query(client, f'file_id "{a.id}"')

    def check_blocks(block_list):
        assert len(block_list) == 2
        assert block_list[0].tags is not None
        assert len(block_list[0].tags) == 1
        assert block_list[0].tags[0].kind == "BlockTag"
        assert block_list[0].text == "A"

    assert blocks.blocks is not None
    check_blocks(blocks.blocks)

    # Let's get the file fresh
    aa = File.get(client, _id=a.id)
    check_blocks(aa.blocks)
    assert aa.tags is not None
    assert len(aa.tags) == 1
    assert aa.tags[0].kind == "FileTag"

    a.delete()


def test_file_upload_with_tags(client: Steamship):
    a = File.create(
        client=client,
        tags=[Tag(kind="FileTag")],
    )
    assert a.id is not None

    query_result = Tag.query(client, f'filetag and file_id "{a.id}"')

    def check_tags(file_tag_list):
        assert len(file_tag_list) == 1
        assert file_tag_list[0] is not None
        assert file_tag_list[0].kind == "FileTag"

    assert query_result.tags is not None
    check_tags(query_result.tags)

    # Let's get the file fresh
    aa = File.get(client, _id=a.id)
    check_tags(aa.tags)

    a.delete()


def test_query(client: Steamship):
    a = File.create(
        client=client,
        blocks=[
            Block(text="A", tags=[Tag(kind="BlockTag")]),
            Block(text="B"),
        ],
    )
    assert a.id is not None
    b = File.create(
        client=client,
        blocks=[Block(text="A"), Block(text="B")],
        tags=[Tag(kind="FileTag")],
    )
    assert b.id is not None

    files = File.query(client=client, tag_filter_query='blocktag and kind "BlockTag"').files
    assert len(files) == 1
    assert files[0].id == a.id

    files = File.query(client=client, tag_filter_query='filetag and kind "FileTag"').files
    assert len(files) == 1
    assert files[0].id == b.id

    # Test serialization; This shouldn't throw
    out_file = File.get(client, _id=b.id)
    json.dumps(out_file.dict())

    a.delete()
    b.delete()


def test_file_list(client: Steamship):
    a = File.create(
        client=client,
        tags=[Tag(kind="FileTag")],
    )
    b = File.create(
        client=client,
        tags=[Tag(kind="FileTag")],
    )
    c = File.create(
        client=client,
        tags=[Tag(kind="FileTag")],
    )

    files = File.list(client=client).files
    assert len(files) == 3
    assert a in files
    assert b in files
    assert c in files

    a.delete()
    b.delete()
    c.delete()


def test_file_refresh(client: Steamship):
    blockifier_path = PLUGINS_PATH / "blockifiers" / "blockifier.py"
    with deploy_plugin(client, blockifier_path, "blockifier") as (
        plugin,
        version,
        instance,
    ):
        file = File.create(client=client, content="This is a test.")
        assert len(file.blocks) == 0
        file.blockify(plugin_instance=instance.handle).wait()
        file.refresh()  # don't reassign file
        assert len(file.blocks) == 4
        file.delete()
