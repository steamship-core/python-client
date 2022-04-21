from steamship import MimeTypes, DocTag
from steamship.base.response import TaskStatus
from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_file_upload_then_parse():
    steamship = _steamship()

    a = steamship.upload(
        content="This is a test."
    ).data
    assert (a.id is not None)

    q1 = a.query().data
    assert (len(q1.blocks) == 0)

    task = a.blockify(pluginInstance="markdown-blockifier-default-1.0")
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.state == TaskStatus.waiting)

    task.wait()
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.state == TaskStatus.succeeded)

    q1 = a.query().data
    assert (len(q1.blocks) == 1)
    assert (q1.blocks[0].text == 'This is a test.')

    b = steamship.upload(
        content="""# Header

This is a test."""
    ).data
    assert (b.id is not None)

    q1 = b.query().data
    assert (len(q1.blocks) == 0)

    task = b.blockify(pluginInstance="markdown-blockifier-default-1.0")
    assert (task.error is None)
    assert (task.task is not None)
    task.wait()

    q1 = b.query().data
    assert (len(q1.blocks) == 2)
    assert (q1.blocks[1].text == 'This is a test.')
    assert (q1.blocks[0].text == 'Header')

    a.delete()
    b.delete()


