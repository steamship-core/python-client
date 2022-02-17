from steamship import BlockTypes, MimeTypes
from steamship.base.response import TaskStatus

from steamship.data.file import FileImportResponse

from .helpers import _random_name, _steamship

import json

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

def test_file_upload_then_parse():
    steamship = _steamship()

    name_a = "{}.txt".format(_random_name())
    a = steamship.upload(
        name=name_a,
        content="This is a test."
    ).data
    assert (a.id is not None)

    q1 = a.query().data
    assert (len(q1.blocks) == 0)

    task = a.convert()
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.taskStatus == TaskStatus.waiting)

    task.wait()
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.taskStatus == TaskStatus.succeeded)

    q1 = a.query().data
    assert (len(q1.blocks) == 2)
    assert (q1.blocks[0].type == BlockTypes.Document)
    assert (q1.blocks[1].type == BlockTypes.Paragraph)
    assert (q1.blocks[1].text == 'This is a test.')

    name_b = "{}.mkd".format(_random_name())
    b = steamship.upload(
        name=name_b,
        content="""# Header

This is a test."""
    ).data
    assert (b.id is not None)

    q1 = b.query().data
    assert (len(q1.blocks) == 0)

    task = b.convert()
    task.wait()

    q1 = b.query().data
    assert (len(q1.blocks) == 3)
    assert (q1.blocks[0].type == BlockTypes.Document)
    assert (q1.blocks[2].type == BlockTypes.Paragraph)
    assert (q1.blocks[2].text == 'This is a test.')
    assert (q1.blocks[1].type == BlockTypes.H1)
    assert (q1.blocks[1].text == 'Header')

    q2 = b.query(blockType=BlockTypes.H1).data
    assert (len(q2.blocks) == 1)
    assert (q2.blocks[0].type == BlockTypes.H1)
    assert (q2.blocks[0].text == 'Header')

    a.delete()
    b.delete()


def test_file_import_response_dict():
    resp = FileImportResponse(bytes=b'some bytes', mimeType=MimeTypes.BINARY)
    to_dict = resp.to_dict()
    from_dict = FileImportResponse.from_dict(to_dict)
    assert (resp.data == from_dict.data)
    assert (resp.mimeType == from_dict.mimeType)


def test_file_import_response_bytes_serialization():
    file_resp = FileImportResponse(bytes=b'some bytes', mimeType=MimeTypes.BINARY)
    to_dict = file_resp.to_dict()
    as_json_string = json.dumps(to_dict)
    as_dict_again = json.loads(as_json_string)
    assert (as_dict_again == to_dict)
