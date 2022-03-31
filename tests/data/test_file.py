import json

from steamship import MimeTypes, DocTag
from steamship.base.response import TaskStatus
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.tags.tag import Tag
from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_file_upload():
    steamship = _steamship()
    name_a = "{}.mkd".format(_random_name())
    a = steamship.upload(
        name=name_a,
        content="A",
        mimeType=MimeTypes.MKD
    ).data
    assert (a.id is not None)
    assert (a.name == name_a)
    assert (a.mimeType == MimeTypes.MKD)

    name_b = "{}.txt".format(_random_name())
    b = steamship.upload(
        name=name_b,
        content="B",
        mimeType=MimeTypes.TXT
    ).data
    assert (b.id is not None)
    assert (b.name == name_b)
    assert (b.mimeType == MimeTypes.TXT)
    assert (a.id != b.id)

    name_c = "{}.txt".format(_random_name())
    c = steamship.upload(
        name=name_c,
        content="B",
        mimeType=MimeTypes.MKD
    ).data
    assert (c.mimeType == MimeTypes.MKD)  # The specified format gets precedence over filename

    d = steamship.upload(
        name=name_c,
        content="B",
    ).data
    assert (d.mimeType == MimeTypes.TXT)  # The filename is used in a pinch.

    a.delete()
    b.delete()
    c.delete()
    d.delete()


def test_file_scrape():
    steamship = _steamship()

    name_a = "{}.html".format(_random_name())
    a = steamship.scrape(
        name=name_a,
        url="https://edwardbenson.com/2020/10/gpt3-travel-agent"
    ).data
    assert (a.id is not None)
    assert (a.name == name_a)
    assert (a.mimeType == MimeTypes.HTML)

    name_b = "{}.html".format(_random_name())
    b = steamship.scrape(
        name=name_b,
        url="https://edwardbenson.com/2018/09/case-of-the-murderous-ai"
    ).data
    assert (b.id is not None)
    assert (a.id != b.id)
    assert (b.name == name_b)
    assert (b.mimeType == MimeTypes.HTML)

    a.delete()
    b.delete()


# def test_file_add_bloc():
#     steamship = _steamship()

#     name_a = "{}.txt".format(_random_name())
#     a = steamship.upload(
#         name=name_a,
#         content="This is a test."
#     )
#     assert(a.id is not None)
#     task  = a.convert()
#     task._run_development_mode()
#     task.wait()
#     q1 = a.query()
#     assert(len(q1.blocks) == 2)

#     # TODO: Append Content
#     # TODO: Append Blocks

def test_file_import_response_dict():
    resp = File.CreateResponse(bytes=b'some bytes', mimeType=MimeTypes.BINARY)
    to_dict = resp.to_dict()
    from_dict = File.CreateResponse.from_dict(to_dict)
    assert (resp.data == from_dict.data)
    assert (resp.mimeType == from_dict.mimeType)


def test_file_import_response_bytes_serialization():
    file_resp = File.CreateResponse(bytes=b'some bytes', mimeType=MimeTypes.BINARY)
    to_dict = file_resp.to_dict()
    as_json_string = json.dumps(to_dict)
    as_dict_again = json.loads(as_json_string)
    assert (as_dict_again == to_dict)


def test_file_upload_with_blocks():
    client = _steamship()
    name_a = "{}.mkd".format(_random_name())
    a = File.create(
        client=client,
        name=name_a,
        blocks=[
            Block.CreateRequest(text="A", tags=[Tag.CreateRequest(name="BlockTag")]),
            Block.CreateRequest(text="B")
        ],
        tags=[
            Tag.CreateRequest(name="FileTag")
        ]
    ).data
    assert (a.id is not None)
    assert (a.name == name_a)

    blocks = Block.listPublic(client, fileId=a.id)

    def check_blocks(blocks):
        assert (len(blocks) == 2)
        assert (blocks[0].tags is not None)
        assert (len(blocks[0].tags) == 1)
        assert (blocks[0].tags[0].name == "BlockTag")
        assert (blocks[0].text == "A")

    assert (blocks.data.blocks is not None)
    check_blocks(blocks.data.blocks)

    # Let's get the file fresh
    aa = File.get(client, id=a.id).data
    check_blocks(aa.blocks)
    assert (aa.tags is not None)
    assert (len(aa.tags) == 1)
    assert (aa.tags[0].name == "FileTag")

    a.delete()
