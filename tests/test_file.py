import pytest
from os import path

from steamship.types.base import TaskStatus
from .helpers import _random_name, _steamship
from steamship import Steamship, BlockTypes, FileFormats

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_file_upload():
    steamship = _steamship()
    name_a = "{}.mkd".format(_random_name())
    a = steamship.upload(
      name=name_a,
      content="A",
      mimeType=FileFormats.MKD
    ).data
    assert(a.id is not None)
    assert(a.name == name_a)
    assert(a.mimeType == FileFormats.MKD)

    name_b = "{}.txt".format(_random_name())
    b = steamship.upload(
        name=name_b,
        content="B",
        mimeType=FileFormats.TXT
    ).data
    assert(b.id is not None)
    assert(b.name == name_b)
    assert(b.mimeType == FileFormats.TXT)
    assert(a.id != b.id)

    name_c = "{}.txt".format(_random_name())
    c = steamship.upload(
        name=name_c,
        content="B",
        mimeType=FileFormats.MKD
    ).data
    assert(c.mimeType == FileFormats.MKD) # The specified format gets precedence over filename

    d = steamship.upload(
        name=name_c,
        content="B",
    ).data
    assert(d.mimeType == FileFormats.TXT) # The filename is used in a pinch.

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
    assert(a.id is not None)
    assert(a.name == name_a)
    assert(a.mimeType == FileFormats.HTML)

    name_b = "{}.html".format(_random_name())
    b = steamship.scrape(
        name=name_b,
        url="https://edwardbenson.com/2018/09/case-of-the-murderous-ai"
    ).data
    assert(b.id is not None)    
    assert(a.id != b.id)
    assert(b.name == name_b)
    assert(b.mimeType == FileFormats.HTML)

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
    assert(a.id is not None)

    q1 = a.query().data
    assert(len(q1.blocks) == 0)

    task = a.convert()
    assert(task.error is None)
    assert(task.task is not None)
    assert(task.task.taskStatus == TaskStatus.waiting)

    task.wait()
    assert(task.error is None)
    assert(task.task is not None)
    assert(task.task.taskStatus == TaskStatus.succeeded)

    q1 = a.query().data
    assert(len(q1.blocks) == 2)
    assert(q1.blocks[0].type == BlockTypes.Document)    
    assert(q1.blocks[1].type == BlockTypes.Paragraph)    
    assert(q1.blocks[1].text == 'This is a test.')

    name_b = "{}.mkd".format(_random_name())
    b = steamship.upload(
        name=name_b,
        content="""# Header

This is a test."""
    ).data
    assert(b.id is not None)

    q1 = b.query().data
    assert(len(q1.blocks) == 0)

    task  = b.convert()
    task.wait()

    q1 = b.query().data
    assert(len(q1.blocks) == 3)
    assert(q1.blocks[0].type == BlockTypes.Document)    
    assert(q1.blocks[2].type == BlockTypes.Paragraph)
    assert(q1.blocks[2].text == 'This is a test.')
    assert(q1.blocks[1].type == BlockTypes.H1)    
    assert(q1.blocks[1].text == 'Header')

    q2 = b.query(blockType=BlockTypes.H1).data
    assert(len(q2.blocks) == 1)
    assert(q2.blocks[0].type == BlockTypes.H1)
    assert(q2.blocks[0].text == 'Header')

    a.delete()
    b.delete()
