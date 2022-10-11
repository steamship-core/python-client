from steamship_tests.utils.fixtures import get_steamship_client

from steamship import File
from steamship.base import TaskState


def test_file_upload_then_parse():
    steamship = get_steamship_client()

    a = File.create(
        steamship,
        content="This is a test.",
    )
    assert a.id is not None

    q1 = a.refresh()
    assert len(q1.blocks) == 0

    task = a.blockify(plugin_instance="markdown-blockifier-default-1.0")
    assert task is not None
    assert task.state == TaskState.waiting

    task.wait()
    assert task is not None
    assert task.state == TaskState.succeeded

    q1 = a.refresh()
    assert len(q1.blocks) == 1
    assert q1.blocks[0].text == "This is a test."

    b = File.create(
        steamship,
        content="""# Header

This is a test.""",
    )
    assert b.id is not None

    q1 = b.refresh()
    assert len(q1.blocks) == 0

    task = b.blockify(plugin_instance="markdown-blockifier-default-1.0")
    task.wait()

    q1 = b.refresh()
    assert len(q1.blocks) == 2
    assert q1.blocks[1].text == "This is a test."
    assert q1.blocks[0].text == "Header"

    a.delete()
    b.delete()
