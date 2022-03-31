from steamship import MimeTypes, DocTag
from steamship.base.response import TaskStatus
from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


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

    task = a.convert(plugin="markdown-converter-default-v1")
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.state == TaskStatus.waiting)

    task.wait()
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.state == TaskStatus.succeeded)

    q1 = a.query().data
    assert (len(q1.blocks) == 2)
    assert (q1.blocks[0].type == DocTag.doc)
    assert (q1.blocks[1].type == DocTag.paragraph)
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

    task = b.convert(plugin="markdown-converter-default-v1")
    assert (task.error is None)
    assert (task.task is not None)
    task.wait()

    q1 = b.query().data
    assert (len(q1.blocks) == 3)
    assert (q1.blocks[0].type == DocTag.doc)
    assert (q1.blocks[2].type == DocTag.paragraph)
    assert (q1.blocks[2].text == 'This is a test.')
    assert (q1.blocks[1].type == DocTag.h1)
    assert (q1.blocks[1].text == 'Header')

    q2 = b.query(blockType=DocTag.h1).data
    assert (len(q2.blocks) == 1)
    assert (q2.blocks[0].type == DocTag.he)
    assert (q2.blocks[0].text == 'Header')

    a.delete()
    b.delete()


