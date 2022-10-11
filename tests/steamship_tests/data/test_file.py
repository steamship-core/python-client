import json

import pytest

from steamship import MimeTypes
from steamship.client import Steamship
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags.tag import Tag


@pytest.mark.usefixtures("client")
def test_file_upload(client: Steamship):
    a = File.create(client=client, content="A", mime_type=MimeTypes.MKD).data
    assert a.id is not None
    assert a.mime_type == MimeTypes.MKD

    b = File.create(client=client, content="B", mime_type=MimeTypes.TXT).data
    assert b.id is not None
    assert b.mime_type == MimeTypes.TXT
    assert a.id != b.id

    a.delete()
    b.delete()


def test_file_import_response_dict():
    resp = File.CreateResponse(_bytes=b"some bytes", mime_type=MimeTypes.BINARY)
    to_dict = resp.dict(include={"data_", "mime_type"})
    file_create_response = File.CreateResponse.parse_obj(to_dict)
    assert resp.data == file_create_response.data
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
            Block.CreateRequest(text="A", tags=[Tag.CreateRequest(kind="BlockTag")]),
            Block.CreateRequest(text="B", tags=[Tag.CreateRequest(kind="BlockTag")]),
        ],
    ).data
    assert a.id is not None

    blocks = Block.query(client, f'file_id "{a.id}"')

    def check_blocks(block_list):
        assert len(block_list) == 2
        assert block_list[0].tags is not None
        assert len(block_list[0].tags) == 1
        assert block_list[0].tags[0].kind == "BlockTag"
        assert block_list[0].text == "A"

    assert blocks.data.blocks is not None
    check_blocks(blocks.data.blocks)

    # Let's get the file fresh
    aa = File.get(client, _id=a.id).data
    check_blocks(aa.blocks)
    a.delete()


def test_file_upload_with_blocks_and_tags(client: Steamship):
    a = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A", tags=[Tag.CreateRequest(kind="BlockTag")]),
            Block.CreateRequest(text="B", tags=[Tag.CreateRequest(kind="BlockTag")]),
        ],
        tags=[Tag.CreateRequest(kind="FileTag")],
    ).data
    assert a.id is not None

    blocks = Block.query(client, f'file_id "{a.id}"')

    def check_blocks(block_list):
        assert len(block_list) == 2
        assert block_list[0].tags is not None
        assert len(block_list[0].tags) == 1
        assert block_list[0].tags[0].kind == "BlockTag"
        assert block_list[0].text == "A"

    assert blocks.data.blocks is not None
    check_blocks(blocks.data.blocks)

    # Let's get the file fresh
    aa = File.get(client, _id=a.id).data
    check_blocks(aa.blocks)
    assert aa.tags is not None
    assert len(aa.tags) == 1
    assert aa.tags[0].kind == "FileTag"

    a.delete()


def test_file_upload_with_tags(client: Steamship):
    a = File.create(
        client=client,
        tags=[Tag.CreateRequest(kind="FileTag")],
    ).data
    assert a.id is not None

    tags = Tag.query(client, f'filetag and file_id "{a.id}"')

    def check_tags(file_tag_list):
        assert len(file_tag_list) == 1
        assert file_tag_list[0] is not None
        assert file_tag_list[0].kind == "FileTag"

    assert tags.data.tags is not None
    check_tags(tags.data.tags)

    # Let's get the file fresh
    aa = File.get(client, _id=a.id).data
    check_tags(aa.tags)

    a.delete()


def test_query(client: Steamship):
    a = File.create(
        client=client,
        blocks=[
            Block.CreateRequest(text="A", tags=[Tag.CreateRequest(kind="BlockTag")]),
            Block.CreateRequest(text="B"),
        ],
    ).data
    assert a.id is not None
    b = File.create(
        client=client,
        blocks=[Block.CreateRequest(text="A"), Block.CreateRequest(text="B")],
        tags=[Tag.CreateRequest(kind="FileTag")],
    ).data
    assert b.id is not None

    files = File.query(client=client, tag_filter_query='blocktag and kind "BlockTag"').data.files
    assert len(files) == 1
    assert files[0].id == a.id

    files = File.query(client=client, tag_filter_query='filetag and kind "FileTag"').data.files
    assert len(files) == 1
    assert files[0].id == b.id

    # Test serialization; This shouldn't throw
    out_file = File.get(client, _id=b.id).data
    json.dumps(out_file.dict())

    a.delete()
    b.delete()
